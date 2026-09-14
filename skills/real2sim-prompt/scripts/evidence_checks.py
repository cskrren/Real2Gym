"""Content-bound evidence checks. No simulator execution or visual judgment."""
import hashlib
import json
import math
from pathlib import Path


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def signature(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


class Evidence:
    def __init__(self, root):
        self.root = Path(root)

    def file(self, ref):
        if not isinstance(ref, dict) or not isinstance(ref.get('path'), str) or not ref['path']:
            raise ValueError('missing evidence file reference')
        p = self.root / ref['path']
        if not p.is_file() or digest(p) != ref.get('sha256'):
            raise ValueError('missing or stale evidence: ' + str(p))
        return p

    def read(self, ref):
        return json.loads(self.file(ref).read_text())

    def inputs(self, inputs):
        required = {'model', 'control', 'initial_state', 'sim_config', 'criteria', 'scenario', 'producer'}
        if not isinstance(inputs, dict) or not required <= inputs.keys():
            raise ValueError('native inputs must include ' + ', '.join(sorted(required)))
        if not isinstance(inputs.get('assets'), list):
            raise ValueError('native inputs require explicit assets list (may be empty)')
        fields = required | ({'review_scene'} if 'review_scene' in inputs else set())
        for k in fields:
            self.file(inputs[k])
        for ref in inputs['assets']:
            self.file(ref)
        # Bind content rather than machine-specific absolute paths.
        return signature({k: sorted(x['sha256'] for x in v) if k == 'assets' else v['sha256'] for k, v in inputs.items() if k in fields or k == 'assets'})

    def display(self, inputs):
        if not isinstance(inputs, dict) or set(inputs) != {'scene', 'render_config', 'producer', 'assets'} or not isinstance(inputs['assets'], list):
            raise ValueError('display_inputs require scene, render_config, producer, assets')
        for k in ('scene', 'render_config', 'producer'):
            self.file(inputs[k])
        for ref in inputs['assets']:
            self.file(ref)
        return signature({k: sorted(r['sha256'] for r in v) if k == 'assets' else v['sha256'] for k, v in inputs.items()})

    def native(self, block, candidate_id):
        if not isinstance(candidate_id, str) or not candidate_id:
            raise ValueError('native candidate_id required')
        if not isinstance(block, dict):
            raise ValueError('native evidence required')
        key = self.inputs(block.get('inputs'))
        run = self.read(block.get('run'))
        trajectory = block.get('trajectory')
        trajectory_path = self.file(trajectory)
        import numpy as np
        with np.load(trajectory_path, allow_pickle=False) as arrays:
            qpos, times = arrays['qpos'], arrays['time_s']
            if qpos.ndim != 2 or len(qpos) < 2 or qpos.shape[1] < 1 or times.shape != (len(qpos),):
                raise ValueError('invalid native trajectory shape')
            if not np.isfinite(qpos).all() or not np.isfinite(times).all() or not (np.diff(times) > 0).all():
                raise ValueError('non-finite trajectory or non-increasing simulation time')
            frame_count = len(qpos)
        result = self.read(block.get('result'))
        if not isinstance(run.get('run_id'), str) or not run['run_id']:
            raise ValueError('missing native run_id')
        if run.get('frame_count') != frame_count:
            raise ValueError('native trajectory frame count mismatch')
        for data in (run, result):
            if data.get('candidate_id') != candidate_id or data.get('inputs_sha256') != key:
                raise ValueError('native candidate/input association mismatch')
            if data.get('run_id') != run['run_id'] or data.get('trajectory_sha256') != trajectory['sha256']:
                raise ValueError('native run/trajectory association mismatch')
        if run.get('mode') != 'native' or run.get('completed') is not True:
            raise ValueError('native run incomplete or replay-only')
        if result.get('criteria_sha256') != block['inputs']['criteria']['sha256']:
            raise ValueError('evaluation criteria mismatch')
        criteria = self.read(block['inputs']['criteria'])
        rules = criteria.get('rules')
        if not isinstance(rules, dict) or not rules or rules.get('task_success') != {'op': 'eq', 'value': True}:
            raise ValueError('criteria must explicitly require task_success=true')
        metrics = result.get('metrics', {})
        if result.get('status') != 'pass':
            raise ValueError('native result not passed')
        for name, rule in rules.items():
            v = metrics.get(name)
            limit = rule.get('value')
            op = rule.get('op')
            if isinstance(limit, bool):
                ok = op == 'eq' and type(v) is bool and v == limit
            else:
                if type(v) not in (int, float) or type(limit) not in (int, float) or not math.isfinite(v) or not math.isfinite(limit):
                    raise ValueError('missing/non-finite metric: ' + name)
                ok = {'le': v <= limit, 'ge': v >= limit, 'eq': v == limit}.get(op, False)
            if not ok:
                raise ValueError('native criterion failed: ' + name)
        return key


def check_scope(record, stage, root):
    scope = record.get('task_scope')
    if scope not in {'static_scene', 'motion_preview', 'native_execution', 'augmentation'}:
        raise ValueError('explicit task_scope required')
    required = scope in {'native_execution', 'augmentation'}
    if type(record.get('physics_required')) is not bool or record['physics_required'] != required:
        raise ValueError('physics_required missing or inconsistent with task_scope')
    if not isinstance(record.get('scope_basis'), str) or not record['scope_basis'].strip():
        raise ValueError('scope_basis required: record requested task scope')
    if stage == 'deliver' and required:
        block = record.get('native_evidence')
        expected = {'path': record.get('scene_path'), 'sha256': record.get('scene_sha256')}
        if not isinstance(block, dict) or block.get('inputs', {}).get('review_scene') != expected:
            raise ValueError('native inputs must bind the current reviewed scene')
        Evidence(root).native(block, record.get('candidate_id'))
