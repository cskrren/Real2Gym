"""Synthetic fixtures test association checks, not physical task success."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
import numpy as np
from PIL import Image
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'skills/real2sim-prompt/scripts'))
from evidence_checks import Evidence, digest, signature, check_scope
from check_augmentation_gate import check
from check_review_gate import check as check_review, Q


class Gates(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.r = Path(self.tmp.name)
        self.e = Evidence(self.r)
        self.counter = 0
        self.parent = self.put({'candidate_id': 'parent', 'parameters': {'mechanical': {'x': 0}, 'appearance': {'color': 'red'}}})
        self.child = self.put({'candidate_id': 'child', 'parameters': {'mechanical': {'x': 0}, 'appearance': {'color': 'blue'}}})
        self.pn = self.native('parent', self.parent)
        self.cn = self.native('child', self.child)
        self.display = {k: self.put({'fixture': k}) for k in ('scene', 'render_config', 'producer')}
        self.display['assets'] = []
        dk = self.e.display(self.display)
        audit = {'candidate_id': 'child', 'inputs_sha256': self.e.inputs(self.cn['inputs']), 'display_inputs_sha256': dk,
                 'checks': {k: {'status': 'pass', 'observation': 'synthetic test only', 'evidence': self.put({'measured': 'synthetic'})}
                            for k in ('support', 'mounting', 'display_collision_alignment')}}
        self.x = {'candidate_id': 'child', 'task_scope': 'augmentation', 'physics_required': True, 'scope_basis': 'synthetic test',
                  'parent_config': self.parent, 'current_config': self.child, 'parent_native': self.pn, 'native_evidence': self.cn,
                  'kind': 'appearance', 'declared_changes': {'/appearance/color': {'before': 'red', 'after': 'blue'}},
                  'scene_audit': self.put(audit), 'display_inputs': self.display, 'media': [], 'required_media': []}
        for renderer in ('blender', 'mujoco'):
            self.counter += 1
            image_path = self.r / f'{self.counter}.png'
            Image.new('RGB', (2, 2), 'blue').save(image_path)
            f = {'path': image_path.name, 'sha256': digest(image_path)}
            camera = self.put({'camera': 'test'})
            key = {'view': 'front', 'frame': 0, 'renderer': renderer}
            receipt = dict(key, candidate_id='child', trajectory_sha256=self.cn['trajectory']['sha256'], display_inputs_sha256=dk,
                           media_sha256=f['sha256'], camera_sha256=camera['sha256'], dimensions=[2, 2], decoded=True, frame_identity_verified=True,
                           validator=self.put({'test_validator': 1}))
            self.x['media'].append(dict(key, file=f, camera=camera, validation=self.put(receipt)))
            self.x['required_media'].append(key)

    def put(self, value):
        self.counter += 1
        p = self.r / f'{self.counter}.json'
        p.write_text(json.dumps(value))
        return {'path': p.name, 'sha256': digest(p)}

    def native(self, cid, scenario):
        inputs = {k: self.put({'synthetic_input': k, 'candidate': cid}) for k in ('model', 'control', 'initial_state', 'sim_config', 'producer')}
        inputs.update(scenario=scenario, assets=[])
        inputs['criteria'] = self.put({'rules': {'task_success': {'op': 'eq', 'value': True}, 'penetration_m': {'op': 'le', 'value': .002}}})
        self.counter += 1
        tp = self.r / f'{self.counter}.npz'
        np.savez(tp, qpos=np.zeros((2, 3)), time_s=np.array([0., .01]))
        traj = {'path': tp.name, 'sha256': digest(tp)}
        common = {'candidate_id': cid, 'inputs_sha256': self.e.inputs(inputs), 'run_id': cid + '-run', 'trajectory_sha256': traj['sha256']}
        run = self.put(dict(common, mode='native', completed=True, frame_count=2))
        result = self.put(dict(common, criteria_sha256=inputs['criteria']['sha256'], status='pass', metrics={'task_success': True, 'penetration_m': .001}))
        return {'inputs': inputs, 'trajectory': traj, 'run': run, 'result': result}

    def gate(self, x=None):
        return check(self.r / self.put(self.x if x is None else x)['path'])

    def mutate_result(self, **values):
        d = self.e.read(self.cn['result']); d.update(values); self.cn['result'] = self.put(d)

    def test_valid_associations(self):
        self.assertTrue(self.gate()['pass'])

    def test_native_flag_is_not_evidence(self):
        with self.assertRaises(ValueError):
            check_scope({'task_scope': 'native_execution', 'physics_required': True, 'scope_basis': 'test', 'physics': {'status': 'pass'}}, 'deliver', self.r)

    def test_missing_or_contradictory_scope(self):
        for scope, required in [(None, False), ('native_execution', False), ('motion_preview', True)]:
            with self.assertRaises(ValueError):
                check_scope({'task_scope': scope, 'physics_required': required, 'scope_basis': 'test'}, 'deliver', self.r)

    def test_explicit_preview(self):
        check_scope({'task_scope': 'motion_preview', 'physics_required': False, 'scope_basis': 'preview requested'}, 'deliver', self.r)

    def test_changed_model_control_initial_or_asset(self):
        for key in ('model', 'control', 'initial_state', 'sim_config', 'producer', 'criteria'):
            b = copy.deepcopy(self.cn); b['inputs'][key] = self.put({'changed': key})
            with self.assertRaises(ValueError): self.e.native(b, 'child')
        b = copy.deepcopy(self.cn); b['inputs']['assets'] = [self.put({'asset': 1})]
        with self.assertRaises(ValueError): self.e.native(b, 'child')

    def test_stale_file(self):
        (self.r / self.cn['trajectory']['path']).write_text('changed')
        with self.assertRaises(ValueError): self.gate()

    def test_result_trajectory_candidate_and_metrics(self):
        original = self.cn['result']
        for changes in ({'trajectory_sha256': 'old'}, {'candidate_id': 'other'}, {'run_id': 'old'}, {'status': 'fail'},
                        {'metrics': {'task_success': True, 'penetration_m': .1}}, {'metrics': {'task_success': True, 'penetration_m': float('nan')}},
                        {'metrics': {'task_success': 1, 'penetration_m': .001}}):
            self.cn['result'] = original; self.mutate_result(**changes)
            with self.assertRaises(ValueError): self.gate()

    def test_undeclared_change(self):
        self.x['declared_changes'] = {}
        with self.assertRaises(ValueError): self.gate()

    def test_support_and_display_evidence(self):
        original = self.x['scene_audit']
        for name in ('support', 'mounting', 'display_collision_alignment'):
            audit = self.e.read(original); audit['checks'][name]['status'] = 'fail'; self.x['scene_audit'] = self.put(audit)
            with self.assertRaises(ValueError): self.gate()
        self.x['scene_audit'] = original
        self.display['scene'] = self.put({'changed': True})
        with self.assertRaises(ValueError): self.gate()

    def test_missing_or_wrong_media(self):
        original = copy.deepcopy(self.x['media'])
        self.x['media'].pop()
        with self.assertRaises(ValueError): self.gate()
        self.x['media'] = original
        receipt = self.e.read(original[0]['validation']); receipt['trajectory_sha256'] = 'old'
        self.x['media'][0]['validation'] = self.put(receipt)
        with self.assertRaises(ValueError): self.gate()

    def test_invalid_image_even_with_matching_hash(self):
        media = self.x['media'][0]
        media['file'] = self.put({'not_image': True})
        with self.assertRaises(OSError): self.gate()

    def test_appearance_cannot_change_mechanics(self):
        c = self.e.read(self.child); c['parameters']['mechanical']['x'] = 1
        self.x['current_config'] = self.put(c)
        self.x['declared_changes']['/mechanical/x'] = {'before': 0, 'after': 1}
        with self.assertRaisesRegex(ValueError, 'mechanical'): self.gate()

    def test_review_gate_regression(self):
        f = self.put({'synthetic': 1})
        x = {'candidate_id': 'child', 'iteration': 0, 'scene_path': f['path'], 'scene_sha256': f['sha256'], 'views': ['front'], 'required_frames': [0],
             'scene_audit': {'status': 'pass', 'evidence': f['path']}, 'records': [{'frame': 0, 'view': 'front', 'image_path': f['path'], 'image_sha256': f['sha256'], 'reviewed': True,
             'questions': {q: {'status': 'pass', 'observation': 'synthetic', 'blocking': False} for q in Q}}], 'issues': [], 'physics': {'status': 'pass'}}
        def run(): return check_review(self.r / self.put(x)['path'], 'deliver')['pass']
        self.assertFalse(run())
        x.update(task_scope='native_execution', physics_required=True, scope_basis='test')
        self.assertFalse(run())
        self.cn['inputs']['review_scene'] = f
        for name in ('run', 'result'):
            receipt = self.e.read(self.cn[name]); receipt['inputs_sha256'] = self.e.inputs(self.cn['inputs'])
            self.cn[name] = self.put(receipt)
        x['native_evidence'] = self.cn
        self.assertTrue(run())
        newer = self.put({'changed_reviewed_scene': True})
        x['scene_path'], x['scene_sha256'] = newer['path'], newer['sha256']
        self.assertFalse(run())


if __name__ == '__main__':
    unittest.main()
