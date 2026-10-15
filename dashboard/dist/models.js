// Browser implementation of simulation/models.py (Models 1-9). Verified against Python fixtures.
export const defaults={
  '1':{m:.5,p:1,F:10,ce:1,ck:1,lam:.5,theta:.5,alpha:2,s0:1,cR:3,cI:2,V:20,b:5,omega:1,gm:1,gp:.2},
  '2':{w:.5,mu:3,r:2,f:3,c:1,H:10},
  '3':{t:3,R:0,a:.5,c:1,d:1,b:1,V:20,cap:10},
  '4':{t:5,c:2,m:.5,f:10,v:50,h:20},
  '5':{N:5,c:.4,B:1,ell:.6,Lloc:1,omega:.5},
  '6':{pH:.1,pL:.5,L:100,f:20,h:20,c:5},
  '7':{s:4,H:10,d:.5,F:2,R:10,rho:1,k:5},
  '8':{w:.5,f:3,r:2,rR:3,p:1,theta:.5,alpha:2,s0:1,lam:.5,cI:2,cR:3,c:1,ck:1,H:10},
  '9':{t:3,R:0,a:.5,c:1,d:1,b:1,cap:10,L:20,f:5,h:2,kappa:4}
};
function optimum(derivative,upper){
  if(derivative(0)<=0)return 0;
  if(derivative(upper)>=0)return upper;
  let lo=0,hi=upper;
  for(let i=0;i<90;i++){const mid=(lo+hi)/2;if(derivative(mid)>0)lo=mid;else hi=mid}
  return (lo+hi)/2;
}
function effort(incentive,cost){
  if(incentive<=0)return 0;
  let hi=1;while(cost*hi<incentive*Math.exp(-hi))hi*=2;
  return optimum(e=>incentive*Math.exp(-e)-cost*e,hi);
}
export function validate(id,p){
  const keys=Object.keys(defaults[id]||{});
  if(!keys.length||Object.keys(p).length!==keys.length||keys.some(k=>!(k in p)))throw Error('Unknown or missing parameter.');
  if(Object.values(p).some(v=>typeof v!=='number'||!Number.isFinite(v)||v<0||v>1e6))throw Error('Use finite values between 0 and 1,000,000.');
  const bounded={'1':['m','lam','theta'],'2':['w'],'3':[],'4':['m'],'5':['omega'],'6':['pH','pL'],'7':['d','rho'],'8':['w','theta','lam'],'9':[]};
  const positive={'1':['ce','ck'],'2':['c','H'],'3':['a','d','V','cap'],'4':['v'],'5':['c','B','ell'],'6':['L','h','c'],'7':['s','d','k'],'8':['c','ck','H'],'9':['a','d','cap','L','h']};
  if(bounded[id].some(k=>p[k]>1))throw Error('Probabilities and bargaining weights must be between 0 and 1.');
  if(positive[id].some(k=>p[k]<=0))throw Error(`These parameters must be positive: ${positive[id].join(', ')}.`);
  if(id==='1'&&p.cR+p.s0<p.cI)throw Error('Continuation model requires cR + s0 ≥ cI.');
  if(id==='5'&&(!Number.isInteger(p.N)||p.N<2))throw Error('Choose an integer number of agencies ≥ 2.');
  if(id==='6'&&!(p.pH<p.pL&&p.f<p.L))throw Error('Require pH < pL and penalty f < harm L.');
  if(id==='8'&&(p.cR+p.s0<p.cI||p.rR+p.s0<p.r))throw Error('Continuation regions require cR + s0 ≥ cI and rR + s0 ≥ r.');
  if(id==='9'&&p.f>=p.L)throw Error('Require penalty f < harm L.');
}
const exp=Math.exp;
function maximize(f,df,lo,hi,points=2001){
  // Grid search, then bisection on the derivative around the best grid point (as in models.py).
  const step=(hi-lo)/(points-1);let best=0,bv=-Infinity;
  for(let i=0;i<points;i++){const v=f(lo+i*step);if(v>bv){bv=v;best=i}}
  let a=lo+Math.max(best-1,0)*step,b=lo+Math.min(best+1,points-1)*step;
  if(df(a)<=0)return a;
  if(df(b)>=0)return b;
  for(let i=0;i<90;i++){const mid=(a+b)/2;if(df(mid)>0)a=mid;else b=mid}
  return (a+b)/2;
}
const functions={
 '1':({m,p,F,ce,ck,lam,theta,alpha,s0,cR,cI,V,b,omega,gm,gp})=>{
  const e=effort(m*F,ce),k=lam*theta*alpha/(ck*(1+p)),failure=exp(-e),sw=s0+alpha*k/(1+p);
  const amendment=cI+theta*(cR+sw-cI),cost=ce*e*e/2+ck*k*k/2+lam*cI,penalty=m*F*failure;
  const initial=cost+penalty-lam*amendment,payments=initial+lam*amendment,gov=(gm*m*m+gp*p*p)/2;
  return {effort:e,dependence:k,success:1-failure,burden:b*failure,switching_cost:sw,amendment_price:amendment,initial_price:initial,negative_initial_bid:initial<0,vendor_revenue:payments,vendor_real_cost:cost,expected_penalty:penalty,vendor_profit:payments-cost-penalty,agency_gross_payment:payments,agency_net_payment_if_penalty_received:payments-penalty,agency_value:V*(1-failure)-payments-omega*b*failure-gov,social_welfare_if_penalty_transfer:V*(1-failure)-cost-b*failure-gov};
 },
 '2':({w,mu,r,f,c,H})=>{
  const D=w*(r+f)-(1-w)*mu,e=effort(D,c),sp=effort(H,c),defect=exp(-e);
  const revenue=defect*(1-w)*(r+mu),cost=c*e*e/2+defect*r,penalty=defect*w*f,social=c*e*e/2+H*defect,best=c*sp*sp/2+H*exp(-sp);
  return {effort:e,public_effort:sp,defect_probability:defect,private_defect_loss:D,vendor_revenue_excluding_fixed:revenue,vendor_real_cost:cost,expected_penalty:penalty,vendor_profit_excluding_fixed:revenue-cost-penalty,agency_gross_payment_excluding_fixed:revenue,social_cost:social,public_social_cost:best,welfare_loss:social-best};
 },
 '3':({t,R,a,c,d,b,V,cap})=>{
  const n=optimum(x=>t-c-d*x+R*a*exp(-a*x),cap),sp=optimum(x=>V*a*exp(-a*x)-c-b-d*x,cap),q=1-exp(-a*n);
  const revenue=t*n+R*q,cost=c*n+d*n*n/2,W=x=>V*(1-exp(-a*x))-(c+b)*x-d*x*x/2;
  return {work:n,public_work:sp,work_gap:n-sp,success:q,vendor_revenue_excluding_fixed:revenue,vendor_real_cost:cost,vendor_profit_excluding_fixed:revenue-cost,burden:b*n,social_welfare:W(n),public_social_welfare:W(sp),welfare_loss:W(sp)-W(n)};
 },
 '4':({t,c,m,f,v,h})=>{
  const tau=m*f?Math.max(0,Math.min(1,1-(t-c)/(m*f))):(t>c?0:1),sp=Math.max(0,Math.min(1,(h+c)/(v+h)));
  const tp=(1-tau*tau)/2,fp=(1-tau)**2/2,W=x=>v*(1-x*x)/2-h*(1-x)**2/2-c*(1-x);
  const revenue=t*(1-tau),cost=c*(1-tau),penalty=m*f*fp;
  return {threshold:tau,public_threshold:sp,flag_rate:1-tau,true_positive_mass:tp,false_positive_mass:fp,false_negative_mass:.5-tp,false_positive_rate:2*fp,vendor_revenue_excluding_fixed:revenue,vendor_real_cost:cost,expected_penalty:penalty,vendor_profit_excluding_fixed:revenue-cost-penalty,applicant_harm:h*fp,social_welfare:W(tau),welfare_loss:W(sp)-W(tau)};
 },
 '5':({N,c,B,ell,Lloc,omega})=>{
  const x=c<B?1-(c/B)**(1/(N-1)):0,no=(1-x)**N,one=N*x*(1-x)**(N-1),W=N*B*(1-no)-c*N*x,best=Math.max(0,N*B-c);
  const omitted=omega*Lloc<ell&&ell<=Lloc,localLoss=omitted?N*(Lloc-ell):0;
  return {test_probability:x,no_test_probability:no,duplicate_test_probability:Math.max(0,1-no-one),expected_tests:N*x,symmetric_equilibrium:c<B?'mixed':'no_test',asymmetric_one_tester_equilibrium:c<=B,selected_welfare:W,coordinated_welfare:best,welfare_loss:best-W,equality_boundary:c===B,local_test:omega*Lloc>=ell,local_test_public:Lloc>=ell,local_welfare_loss:localLoss,total_welfare_loss:best-W+localLoss};
 },
 '6':({pH,pL,L,f,h,c})=>{
  const rh=h<pH*(L-f),rl=h<pL*(L-f),high=c+f*pH*(!rh)<f*pL*(!rl),p=high?pH:pL,review=high?rh:rl;
  const real=c*high+h*review,harm=p*L*(!review),sp=Math.min(c+Math.min(h,pH*L),Math.min(h,pL*L)),penalty=f*p*(!review);
  return {high_effort:high,review,review_after_high:rh,review_after_low:rl,raw_error:p,final_error:p*(!review),vendor_real_cost:c*high,expected_penalty:penalty,vendor_profit_excluding_fixed:-c*high-penalty,agency_review_cost:h*review,agency_net_cost_excluding_fixed:h*review+harm-penalty,social_cost:real+harm,public_social_cost:sp,welfare_loss:real+harm-sp};
 },
 '7':({s,H,d,F,R,rho,k})=>{
  const sanction=d*(F+rho*R),threshold=sanction?s/sanction:null,feasible=threshold!==null&&threshold<=1;
  const deter=feasible&&k*threshold<H,audit=deter?threshold:0,cost=deter?k*audit:H-s,best=feasible?Math.min(H-s,k*threshold):H-s;
  return {minimum_audit:threshold,deterrence_feasible:feasible,selected_audit:audit,substitutes:!deter,vendor_cost_saving:deter?0:s,public_harm:deter?0:H,audit_cost:k*audit,agency_cost:k*audit+(deter?0:H),social_cost:cost,best_feasible_policy_social_cost:best,policy_welfare_loss:cost-best};
 },
 '8':({w,f,r,rR,p,theta,alpha,s0,lam,cI,cR,c,ck,H})=>{
  const sw=k=>s0+alpha*k/(1+p),margin=k=>theta*(rR+sw(k)-r),bestK=e=>theta*alpha*(lam+(1-w)*exp(-e))/(ck*(1+p));
  const payoff=(e,k)=>-c*e*e/2-ck*k*k/2+lam*theta*(cR+sw(k)-cI)+exp(-e)*((1-w)*margin(k)-w*(r+f));
  const slope=e=>-c*e+exp(-e)*(w*(r+f)-(1-w)*margin(bestK(e))),e=maximize(x=>payoff(x,bestK(x)),slope,0,Math.max(w*(r+f)/c,0)+1),k=bestK(e),defect=exp(-e),mu=margin(k);
  const amendment=cI+theta*(cR+sw(k)-cI),repairs=(1-w)*defect,cont=lam*amendment+repairs*(r+mu);
  const cost=c*e*e/2+ck*k*k/2+lam*cI+defect*r,penalty=defect*w*f,initial=cost+penalty-cont,sp=effort(H,c);
  const social=c*e*e/2+ck*k*k/2+lam*cI+H*defect,best=c*sp*sp/2+lam*cI+H*exp(-sp);
  return {effort:e,dependence:k,defect_probability:defect,public_effort:sp,switching_cost:sw(k),repair_margin:mu,repair_price:r+mu,private_defect_loss:w*(r+f)-(1-w)*mu,amendment_price:amendment,paid_repair_probability:repairs,continuation_revenue:cont,initial_price:initial,negative_initial_bid:initial<0,vendor_real_cost:cost,expected_penalty:penalty,agency_gross_payment:initial+cont,vendor_profit:initial+cont-cost-penalty,social_cost:social,public_social_cost:best,welfare_loss:social-best};
 },
 '9':({t,R,a,c,d,b,cap,L,f,h,kappa})=>{
  const net=L-f-kappa,cutoff=net>=h?Math.log(net/h)/a:-1;
  const base=n=>(t-c)*n-d*n*n/2+R*(1-exp(-a*n)),dbase=n=>t-c-d*n+R*a*exp(-a*n),options=[];
  if(cutoff>=0){const n=optimum(dbase,Math.min(cutoff,cap));options.push([base(n),1,n])}
  if(cutoff<cap){const lo=Math.max(cutoff,0),n=lo+optimum(x=>dbase(lo+x)+f*a*exp(-a*(lo+x)),cap-lo);if(n>cutoff)options.push([base(n)-f*exp(-a*n),0,n])}
  const [,reviewing,n]=options.reduce((best,o)=>o[0]>best[0]||(o[0]===best[0]&&o[1]>best[1])?o:best);
  const raw=exp(-a*n),cost=(x,rv)=>(c+b)*x+d*x*x/2+(rv?h+kappa*exp(-a*x):L*exp(-a*x));
  const withReview=optimum(x=>kappa*a*exp(-a*x)-c-b-d*x,cap),without=optimum(x=>L*a*exp(-a*x)-c-b-d*x,cap);
  const pub=[[cost(withReview,1),1,withReview],[cost(without,0),0,without]].reduce((best,o)=>o[0]<best[0]||(o[0]===best[0]&&o[1]<best[1])?o:best);
  const revenue=t*n+R*(1-raw),real=c*n+d*n*n/2,penalty=reviewing?0:f*raw,social=cost(n,reviewing);
  return {work:n,review:!!reviewing,review_cutoff_work:Math.max(cutoff,0),raw_error:raw,final_error:reviewing?0:raw,vendor_revenue_excluding_fixed:revenue,vendor_real_cost:real,expected_penalty:penalty,vendor_profit_excluding_fixed:revenue-real-penalty,agency_review_cost:reviewing?h+kappa*raw:0,burden:b*n,public_work:pub[2],public_review:!!pub[1],social_cost:social,public_social_cost:pub[0],welfare_loss:social-pub[0]};
 }
};
export function solve(id,overrides={}){id=String(id);const p={...defaults[id],...overrides};validate(id,p);return functions[id](p)}
