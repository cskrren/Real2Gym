#!/usr/bin/env python3
"""Stage-three evidence gate; does not require paired real RGB."""
import argparse
import json
from pathlib import Path
from evidence_checks import Evidence, signature


def flatten(x, prefix=''):
    if isinstance(x, dict):
        result = {}
        for k, v in x.items():
            if '/' in k:
                raise ValueError('configuration keys must not contain /')
            result.update(flatten(v, prefix + '/' + k))
        return result
    return {prefix: x}


def check(path):
    path = Path(path)
    x = json.loads(path.read_text())
    e = Evidence(path.parent)
    cid = x.get('candidate_id')
    if not isinstance(cid, str) or not cid:
        raise ValueError('candidate_id required')
    if x.get('task_scope') != 'augmentation' or x.get('physics_required') is not True:
        raise ValueError('augmentation requires native execution')
    if not isinstance(x.get('scope_basis'), str) or not x['scope_basis'].strip():
        raise ValueError('scope_basis required')
    parent = e.read(x['parent_config'])
    current = e.read(x['current_config'])
    if parent.get('candidate_id') == cid or current.get('candidate_id') != cid:
        raise ValueError('invalid parent/child identity')
    for config in (parent, current):
        if not isinstance(config.get('parameters'), dict) or not config['parameters']:
            raise ValueError('nonempty parameters required')
    before, after = flatten(parent['parameters']), flatten(current['parameters'])
    if before.keys() != after.keys():
        raise ValueError('parameter schema change requires explicit migration')
    actual = {k: {'before': before[k], 'after': after[k]} for k in before if before[k] != after[k]}
    changes = x.get('declared_changes')
    if not isinstance(changes, dict) or signature(changes) != signature(actual):
        raise ValueError('undeclared or incorrect parameter changes')
    kind = x.get('kind')
    if kind not in {'mechanical', 'appearance'} or not actual:
        raise ValueError('nonempty mechanical/appearance augmentation required')
    if kind == 'appearance':
        allowed = ('/appearance/', '/environment/')
        if any(not k.startswith(allowed) for k in actual):
            raise ValueError('appearance child changed mechanical parameters')
    # Parent acceptance must bind the parent configuration, not a naked pass flag.
    if x['parent_native']['inputs']['scenario'] != x['parent_config']:
        raise ValueError('parent native scenario differs from parent config')
    e.native(x['parent_native'], parent['candidate_id'])
    native = x['native_evidence']
    if native['inputs']['scenario'] != x['current_config']:
        raise ValueError('child native scenario differs from current config')
    key = e.native(native, cid)
    audit = e.read(x['scene_audit'])
    if audit.get('inputs_sha256') != key or audit.get('candidate_id') != cid:
        raise ValueError('stale scene audit')
    display_key = e.display(x['display_inputs'])
    if audit.get('display_inputs_sha256') != display_key:
        raise ValueError('scene audit display assets mismatch')
    for name in ('support', 'mounting', 'display_collision_alignment'):
        row = audit.get('checks', {}).get(name, {})
        if row.get('status') != 'pass' or not row.get('observation'):
            raise ValueError('scene audit missing/failed: ' + name)
        e.file(row.get('evidence'))
    expected = x.get('required_media')
    if not isinstance(expected, list) or not expected:
        raise ValueError('explicit nonempty required_media required')
    wanted = {(r['view'], r['frame'], r['renderer']) for r in expected}
    if len(wanted) != len(expected) or any(r not in {'blender', 'mujoco'} for _, _, r in wanted):
        raise ValueError('invalid/duplicate media coverage')
    fv = {(v, f) for v, f, _ in wanted}
    if any((v, f, r) not in wanted for v, f in fv for r in ('blender', 'mujoco')):
        raise ValueError('both Blender and MuJoCo required for each frame/view')
    found = set()
    for media in x.get('media', []):
        k = (media['view'], media['frame'], media['renderer'])
        if k in found:
            raise ValueError('duplicate media')
        found.add(k)
        from PIL import Image
        with Image.open(e.file(media['file'])) as im:
            dimensions = list(im.size)
            im.verify()
        e.file(media['camera'])
        receipt = e.read(media['validation'])
        bindings = {'candidate_id': cid, 'trajectory_sha256': native['trajectory']['sha256'],
                    'display_inputs_sha256': display_key, 'media_sha256': media['file']['sha256'],
                    'camera_sha256': media['camera']['sha256'], 'dimensions': dimensions, 'view': k[0], 'frame': k[1], 'renderer': k[2]}
        if any(receipt.get(a) != b for a, b in bindings.items()):
            raise ValueError('media identity mismatch')
        if receipt.get('decoded') is not True or receipt.get('frame_identity_verified') is not True:
            raise ValueError('media validation incomplete')
        e.file(receipt.get('validator'))
    if found != wanted:
        raise ValueError('missing/extra required media')
    return {'candidate_id': cid, 'pass': True, 'media_count': len(found), 'errors': []}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('record')
    args = parser.parse_args()
    try:
        result = check(args.record)
    except (OSError, ValueError, TypeError, KeyError, AttributeError) as exc:
        result = {'pass': False, 'errors': [str(exc)]}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result['pass'] else 2)
