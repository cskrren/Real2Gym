#!/usr/bin/env python3
"""Validate evidence coverage and stage boundaries, never generate visual judgments."""
from pathlib import Path
from evidence_checks import check_scope
import argparse,hashlib,json,sys
Q=('largest_difference','camera_alignment','relative_object_alignment','penetration_and_contact','reconstruction_fidelity')
GOOD={'pass','pass_with_notes'};ALL=GOOD|{'observed','fail','review','not_evaluated'}
def check_instances(path,views,stage):
 p=Path(path);x=json.loads(p.read_text());errors=[];strict=stage!='review'
 def bad(msg):errors.append('instances: '+msg)
 def evidence(row,key,required=False):
  name=row.get(key);digest=row.get(key.replace('_path','')+'_sha256' if key.endswith('_path') else key+'_sha256')
  if not name and not digest:
   if required:bad('missing '+key)
   return
  if not isinstance(name,str) or not isinstance(digest,str):bad('missing path/hash '+key);return
  f=p.parent/name
  if not f.is_file():bad('missing file '+name)
  elif hashlib.sha256(f.read_bytes()).hexdigest()!=digest:bad('stale hash '+name)
 if set(x.get('views',[]))!=set(views):bad('view coverage differs from gate')
 evidence(x,'inventory_evidence',strict)
 if strict and (x.get('inventory_reviewed')is not True or x.get('unassigned_visible_regions')!=[]):bad('inventory incomplete or unreviewed')
 instances=x.get('instances',[]);ids=[r.get('id') for r in instances]
 if not instances or len(ids)!=len(set(ids)) or any(not i for i in ids):bad('empty/duplicate/missing instance IDs')
 for r in instances:
  label=str(r.get('id'))
  if not r.get('semantic_label') or r.get('role')not in {'interaction','support','robot','background'}:bad('invalid label/role '+label)
  for key in ['identity_status','geometry_status']:
   if not r.get(key):bad('missing '+key+' '+label)
   elif strict and r[key]not in GOOD:bad(key+' not passed '+label)
  obs=r.get('observations',{})
  if set(obs)!=set(views):bad('missing/extra observation views '+label)
  for v,a in obs.items():
   vis=a.get('visibility')
   if vis not in {'visible','partially_occluded','occluded','out_of_frame','unknown'}:bad('invalid visibility '+label+' '+v)
   if strict and (vis=='unknown' or a.get('status')not in GOOD):bad('unresolved observation '+label+' '+v)
   if vis in {'visible','partially_occluded'}:
    evidence(a,'mask_path',strict)
    if strict and not a.get('mask_source'):bad('mask provenance missing '+label+' '+v)
   elif not a.get('reason'):bad('visibility reason missing '+label+' '+v)
  evidence(r,'mesh_path',strict)
  if r.get('role')=='robot':
   evidence(r,'description_path',strict);evidence(r,'structure_evidence',strict)
   if strict and (r.get('structure_status')not in GOOD or r.get('alignment_status')not in GOOD):bad('robot structure/alignment not passed '+label)
  else:
   evidence(r,'cloud_path',strict and not r.get('cloud_unavailable_reason'))
   if strict and not r.get('geometry_source'):bad('geometry provenance missing '+label)
 return errors
def check(path,stage):
 p=Path(path);root=p.parent;x=json.loads(p.read_text());errors=[]
 def bad(msg):errors.append(msg)
 def filehash(name,digest):
  if not name or not digest:bad('missing evidence path/hash');return
  f=root/name
  if not f.is_file():bad('missing file: '+name)
  elif hashlib.sha256(f.read_bytes()).hexdigest()!=digest:bad('stale hash: '+name)
 if type(x.get('iteration')) is not int or x['iteration']<0:bad('iteration must be a nonnegative integer')
 filehash(x.get('scene_path'),x.get('scene_sha256'))
 views=x.get('views',[]);frames=x.get('required_frames',[])
 if not views or not frames:bad('empty required coverage')
 init=x.get('initial_alignment')
 if init is not None:
  if init.get('required') is not True:bad('initial alignment cannot be disabled after declaring initialization')
  if init.get('frame') not in frames:bad('initial alignment frame missing from required coverage')
  if not init.get('method'):bad('initialization method missing')
  filehash(init.get('evidence'),init.get('evidence_sha256'))
  if stage!='review' and init.get('status') not in GOOD:bad('initial alignment gate not passed')
  if init.get('mode')=='instance_first' or init.get('method')=='Pi3X+semantic_instances':
   filehash(init.get('instance_manifest'),init.get('instance_manifest_sha256'))
   manifest=root/(init.get('instance_manifest') or '')
   if manifest.is_file():errors.extend(check_instances(manifest,views,stage))
 expected={(f,v)for f in frames for v in views};actual={};issues=x.get('issues',[])
 for r in x.get('records',[]):
  k=(r.get('frame'),r.get('view'))
  if k in actual:bad('duplicate frame/view '+str(k))
  actual[k]=r;filehash(r.get('image_path'),r.get('image_sha256'))
  if r.get('reviewed')is not True:bad('not visually reviewed '+str(k))
  qs=r.get('questions',{})
  for q in Q:
   a=qs.get(q,{})
   if a.get('status')not in ALL or not str(a.get('observation','')).strip() or not isinstance(a.get('blocking'),bool):bad('missing/invalid question '+str(k)+' '+q);continue
   if q!='largest_difference' and a['status']=='observed':bad('observed invalid for required judgment '+str(k)+' '+q)
   if a['blocking'] or a['status']in {'fail','review','not_evaluated'}:
    matching=[i for i in issues if i.get('question')==q and k[0]in i.get('frames',[]) and k[1]in i.get('views',[])]
    if not matching:bad('untracked feedback '+str(k)+' '+q)
   if stage!='review' and (a['blocking'] or (q in Q[1:4] and a['status']not in GOOD)):bad('stage blocked '+str(k)+' '+q)
 missing=expected-set(actual)
 if missing:bad('missing frame/view records: '+str(sorted(missing)))
 audit=x.get('scene_audit',{})
 if not audit.get('status') or not audit.get('evidence'):bad('scene audit missing')
 elif not (root/audit['evidence']).is_file():bad('scene audit evidence missing')
 if stage!='review' and audit.get('status')not in GOOD:bad('scene audit not passed')
 ids=[i.get('id')for i in issues]
 if len(ids)!=len(set(ids)) or None in ids:bad('duplicate/missing issue ids')
 for i in issues:
  if not all(i.get(k)for k in ['question','frames','views','observation','expected','proposed_parameters','status']):bad('incomplete issue '+str(i.get('id')))
  if i.get('status') in ['resolved','accepted_by_user']:
   if not i.get('resolution') or not i.get('checked_window') or not i.get('evidence'):bad('issue closed without recheck '+str(i.get('id')))
   for key in i.get('evidence',[]):
    if key not in {str(f)+':'+v for f,v in actual}:bad('closed issue references absent current record '+key)
   if i.get('status')=='accepted_by_user' and not i.get('user_acceptance_quote'):bad('user acceptance missing')
  elif stage!='review' and i.get('blocking'):bad('open blocking issue '+str(i.get('id')))
 if x.get('iteration',0)>0:
  if not x.get('changed_parameters') or not x.get('addressed_issue_ids'):bad('correction missing changes/feedback link')
 try:check_scope(x,stage,root)
 except (OSError,ValueError,TypeError,KeyError,AttributeError) as e:bad(str(e))
 return {'candidate_id':x.get('candidate_id'),'stage':stage,'pass':not errors,'required_frame_views':len(expected),'provided_frame_views':len(actual),'errors':errors}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('record');p.add_argument('--stage',choices=['review','physics','deliver'],default='review');a=p.parse_args()
 try:r=check(a.record,a.stage)
 except (OSError,ValueError,TypeError,KeyError) as e:r={'pass':False,'errors':['invalid record: '+str(e)]}
 print(json.dumps(r,ensure_ascii=False,indent=2));sys.exit(0 if r['pass'] else 2)
