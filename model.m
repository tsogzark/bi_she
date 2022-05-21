function dy=model(t,v)
  dy=zeros(25,1);
  s_i=v(1);
  a=v(2);
  r=v(3);
  e_t=v(4);
  e_m=v(5);
  q=v(6);
  m_r=v(7);
  m_t=v(8);
  m_m=v(9);
  m_q=v(10);
  c_r=v(11);
  c_t=v(12);
  c_m=v(13);
  c_q=v(14);
  zm_r=v(15);
  zm_t=v(16);
  zm_m=v(17);
  zm_q=v(18);
  N=v(19);
  s=v(20);
  c=v(21);
  m_c=v(22);
  c_c=v(23);
  zm_c=v(24);
  cl_ext=v(25);

  theta_r=426.87;
  theta_t=4.38;
  theta_m=4.38;
  theta_q=4.38;
  theta_c=4.38;
  w_t=4.14;
  w_m=4.14;
  w_r=930;
  k_cm=0.00599;
  w_q=948.93;
  w_p=0;
  w_c=4.14;
  gm_max=1260.0;
  k_gm=7;
  v_t=760;
  k_t=1000;
  v_m=5800;
  k_m=1000;
  k_q=152219;
  h_q=4;
  n_r=7549;
  n_t=300;
  n_m=300;
  n_q=300;
  n_s=0.5;
  n_c=300;
  b=0;
  d_m=0.1;
  k_b=1;
  k_u=1;
  M=100000000;
  d_N=0; %不考虑死亡
  d_s=0; %流出为0
  k_in=10e20; %流入为无限大
  gm_a=gm_max*a/(k_gm+a);
  lam=gm_a*(c_r+c_q+c_t+c_m)/M;
  v_max_div_k=5.8/0.62*lam*60;
  if cl_ext<v_max_div_k
    cl=cl_ext/(1 + v_max_div_k*12);
  else
    cl=cl_ext-v_max_div_k;
  end
  

  %ds_i,v(1);
  dy(1)=e_t*(v_t*s/(s+k_t))-e_m*v_m*s_i/(s_i+k_m)-lam*s_i;
  %da,v(2);
  dy(2)=n_s*e_m*v_m*s_i/(s_i+k_m)-(c_r+c_t+c_m+c_q)*gm_a-lam*a;
  %dr,v(3);
  dy(3)=gm_a/n_r*c_r-lam*r+gm_a/n_r*c_r-k_b*r*m_r+k_u*c_r+gm_a/n_t*c_t-k_b*r*m_t+k_u*c_t+gm_a/n_m*c_m-k_b*r*m_m+k_u*c_m+gm_a/n_q*c_q-k_b*r*m_q+k_u*c_q+gm_a/n_c*c_c-k_b*r*m_c;
  %de_t,v(4);
  dy(4)=gm_a/n_t*c_t-lam*e_t;
  %de_m,v(5);
  dy(5)=gm_a/n_m*c_m-lam*e_m;
  %dq,v(6);
  dy(6)=gm_a/n_m*c_m-lam*e_m;
  %dm_r,v(7);
  dy(7)=w_r*a/(theta_r+a)-lam*m_r-d_m*m_r+gm_a/n_r*c_r-k_b*r*m_r+k_u*c_r;
  %dm_t,v(8);
  dy(8)=w_t*a/(theta_t+a)-lam*m_t-d_m*m_t+gm_a/n_t*c_t-k_b*r*m_t+k_u*c_t;
  %dm_m,v(9);
  dy(9)=w_m*a/(theta_m+a)-lam*m_m-d_m*m_m+gm_a/n_m*c_m-k_b*r*m_m+k_u*c_m;
  %dm_q,v(10);
  dy(10)=w_q*a/(theta_q+a)*1/(1+(q/k_q)^h_q)-lam*m_q-d_m*m_q+gm_a/n_q*c_q-k_b*r*m_q+k_u*c_q;
  %dc_r,v(11);
  dy(11)=k_b*r*m_r-k_u*c_r-gm_a/n_r*c_r-lam*c_r-c_r*cl*k_cm;
  %dc_t,v(12);
  dy(12)=k_b*r*m_t-k_u*c_t-gm_a/n_t*c_t-lam*c_t-c_t*cl*k_cm;
  %dc_m,v(13);
  dy(13)=k_b*r*m_m-k_u*c_m-gm_a/n_m*c_m-lam*c_m-c_m*cl*k_cm;
  %dc_q,v(14);
  dy(14)=k_b*r*m_q-k_u*c_q-gm_a/n_q*c_q-lam*c_q-c_q*cl*k_cm;
  %dzm_r,v(15);
  dy(15)=c_r*cl*k_cm-lam*zm_r;
  %dzm_t,v(16);
  dy(16)=c_t*cl*k_cm-lam*zm_t;
  %dzm_m,v(17);
  dy(17)=c_m*cl*k_cm-lam*zm_m;
  %dzm_q,v(18);
  dy(18)=c_m*cl*k_cm-lam*zm_m;
  %dN,v(19);
  dy(19)=lam*N-d_N*N;
  %ds,v(20);
  dy(20)=k_in-e_t*v_t*s/(s+k_t)*N-d_s*s;
  %dc,v(21)
  dy(21)=gm_a/n_c*c_c-lam*c;
  %dm_c,v(22)
  dy(22)=w_c*a/(theta_c+a)-lam*m_c-d_m*m_c+gm_a/n_c*c_c-k_b*r*m_c+k_u*c_c;
  %dc_c,v(23)
  dy(23)=k_b*r*m_c-k_u*c_c-gm_a/n_c*c_c-lam*c_c-c_c*cl*k_cm;
  %dzm_c,v(24)
  dy(24)=c_c*cl*k_cm-lam*zm_c;
