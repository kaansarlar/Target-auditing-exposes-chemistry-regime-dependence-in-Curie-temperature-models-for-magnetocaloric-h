"""Recompute reported point metrics from saved out-of-fold predictions."""
from pathlib import Path
import argparse,json
import numpy as np,pandas as pd
from sklearn.metrics import r2_score,mean_squared_error,mean_absolute_error,confusion_matrix,matthews_corrcoef

ROOT=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('--output-dir',type=Path,default=ROOT/'results');args=ap.parse_args();OUTPUT=args.output_dir.resolve()
def reg(y,p):return {'r2':r2_score(y,p),'rmse':mean_squared_error(y,p)**.5,'mae':mean_absolute_error(y,p)}
def close(a,b):assert np.isclose(a,b,atol=1e-9,rtol=1e-9),(a,b)

d=pd.read_csv(ROOT/'data/strict_experimental_tc_72.csv')
assert len(d)==72 and d.reference_id.nunique()==25
assert not d.reference_id.eq('[15]').any()
assert not d.source_row.duplicated().any()
aud=pd.read_csv(ROOT/'data/record_audit_141_conservative.csv')
assert len(aud)==141 and aud.reference_id.eq('[15]').sum()==7
summary=pd.read_csv(OUTPUT/'strict_tc_grouped_cv/strict_model_summary.csv')
assert len(summary)==7 and summary.n_records.eq(72).all() and summary.n_references.eq(25).all()
assert summary.loc[summary.model.ne('DummyMean'),'candidate_budget'].eq(60).all()
oof=pd.read_csv(OUTPUT/'strict_tc_grouped_cv/strict_oof_predictions.csv')
for name,z in oof.groupby('model'):
 assert len(z)==72 and z.source_row.nunique()==72 and z.y_pred_TC.notna().all()
 s=summary[summary.model.eq(name)].iloc[0];m=reg(z.y_true_TC,z.y_pred_TC)
 for k,v in m.items():close(v,s['oof_'+k])
 splits=pd.read_csv(OUTPUT/'strict_tc_grouped_cv/strict_split_audit.csv')
 splits=splits[splits.model.eq(name)]
 assert len(splits)==10
 for row in splits.itertuples():assert not set(row.train_references.split(';'))&set(row.test_references.split(';'))
repeat=pd.read_csv(OUTPUT/'strict_tc_robustness/repeated_partition_metrics.csv')
pred=pd.read_csv(OUTPUT/'strict_tc_robustness/repeated_partition_oof.csv')
assert set(repeat.seed)==set(range(5)) and len(pred)==360
for seed,z in pred.groupby('seed'):
 assert len(z)==72 and z.source_row.nunique()==72
 s=repeat[repeat.seed.eq(seed)].iloc[0]
 close(r2_score(z.TC,z.prediction_K),s.r2)
 close(r2_score(z.TC,z.family_mean_prediction_K),s.family_mean_r2)
 for fold,t in z.groupby('fold'):
  assert not set(t.reference_id)&set(z.loc[z.fold.ne(fold),'reference_id'])
  means=z[z.fold.ne(fold)].groupby('chemistry_family').TC.mean()
  want=t.chemistry_family.map(means).fillna(z.loc[z.fold.ne(fold),'TC'].mean())
  assert np.allclose(want,t.family_mean_prediction_K)
cl=pd.read_csv(OUTPUT/'strict_tc_classification/direct_classifier_summary.csv')
co=pd.read_csv(OUTPUT/'strict_tc_classification/direct_classifier_oof.csv')
for name,z in co.groupby('model'):
 assert len(z)==72 and z.source_row.nunique()==72
 s=cl[cl.model.eq(name)].iloc[0];tn,fp,fn,tp=confusion_matrix(z.target,z.prediction,labels=[0,1]).ravel()
 assert (tn,fp,fn,tp)==(s.tn,s.fp,s.fn,s.tp)
 close(matthews_corrcoef(z.target,z.prediction),s.mcc)
pr=pd.read_csv(OUTPUT/'strict_tc_process_phase/process_phase_model_comparison.csv')
assert pr.n_records.eq(64).all() and pr.n_references.eq(23).all()
for s in pr.itertuples():
 z=pd.read_csv(OUTPUT/f'strict_tc_process_phase/oof_predictions__{s.feature_set}.csv')
 assert len(z)==64 and z.source_row.nunique()==64
 m=reg(z.TC,z.y_pred_TC)
 for k,v in m.items():close(v,getattr(s,'oof_'+k))
report={'status':'PASS','primary_records':72,'primary_publications':25,'models':7,'repeat_seeds':5,'classifiers':5,'paired_records':64,'paired_publications':23,'checks':['target-filter counts','unique record identities','group separation','saved OOF regression metrics','training-only family baseline','classification confusion counts','process-phase point metrics']}
(OUTPUT/'verification_report.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
