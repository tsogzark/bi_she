s_i0=1000; %1
a0=1000; %2
r0=20000; %3
e_t0=20000; %4
e_m0=20000; %5
q0=20000; %6
m_r0=0; %7
m_t0=0; %8
m_m0=0; %9
m_q0=0; %10
c_r0=0; %11
c_t0=0; %12
c_m0=0; %13
c_q0=0; %14
zm_r0=0; %15
zm_t0=0; %16
zm_m0=0; %17
zm_q0=0; %18
N0=1; %19
s0=0; %20
c0=0; %21
m_c0=0; %22
c_c0=0; %23
zm_c0=0; %24
k_cm=0.00599;



init=[s_i0;a0;r0;e_t0;e_m0;q0;m_r0;m_t0;m_m0;m_q0;c_r0;c_t0;c_m0;c_q0;zm_r0;zm_t0;zm_m0;zm_q0;N0;s0;c0;m_c0;c_c0;zm_c0;0;];
dim=21;
t0=0;
tf=200;
timesteps=200;
[T,v]=ode15s(@model,linspace(t0,tf,timesteps),init);
re=v(:,dim);
for n=linspace(0,100,100)
init=[s_i0;a0;r0;e_t0;e_m0;q0;m_r0;m_t0;m_m0;m_q0;c_r0;c_t0;c_m0;c_q0;zm_r0;zm_t0;zm_m0;zm_q0;N0;s0;c0;m_c0;c_c0;zm_c0;n;];
  [T,v]=ode15s(@model,linspace(t0,tf,timesteps),init);
  re=[re,v(:,dim)];
end
csvwrite('data.csv', re(20,:));
plot(re(20,:));
set(gca, 'fontsize', 20);
set(gca, 'xTick', 0:10:100);
set(gca, 'xTicklabel', 0:5:50);
xlabel('Kanamycin/(mg/L)');
ylabel('Proteins/cell');
% ylabel('Time/min');
