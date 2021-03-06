clear, clc

CodeRate = 5/6; % can be 1/2, 2/3, 3/4 or 5/6
Mqam = 16;  % can be 4, 16, 64 for '802-11'
    Mask = sqrt(Mqam);
Ncoded = 648;  % can be 648, 1299, 1944
    Ninfo = CodeRate*Ncoded;
    
% Simulation Parameters
SNRdB     = 1:8;
    lenSNR    = length(SNRdB);
SNR       = 10.^(SNRdB/10);
Nsims = 1;
MinFramError = 100;
MaxFramSimtd = 1e4;

% Modulation
QAMMOD  = comm.RectangularQAMModulator('ModulationOrder',Mqam,...
    'BitInput',true,'NormalizationMethod','Average power');

% Coding
Hldpc      = WL11_LDPCmatrix(CodeRate,Ncoded);
Hsprs      = sparse(Hldpc);
LDPCENC = comm.LDPCEncoder('ParityCheckMatrix',Hsprs);
try
    LDPCDEC = comm.gpu.LDPCDecoder('ParityCheckMatrix',Hsprs,'MaximumIterationCount',20);
catch
    LDPCDEC = comm.LDPCDecoder('ParityCheckMatrix',Hsprs,'MaximumIterationCount',20);
end
Data = randi([0 1],Ninfo,1);
Coded = LDPCENC(Data);

% Keep track
ProbFerr  = zeros(lenSNR,Nsims);
ProbBerr  = zeros(lenSNR,Nsims);
AvgEstSNR = zeros(lenSNR,Nsims);

ProbBerrPy = zeros(lenSNR, Nsims);
ProbFerrPy = zeros(lenSNR, Nsims);
%decodercfg = lpdcDecoderConfig(Hsprs, 'norm-min-sum')
%%
% Transmit message with different SNR
for iSNR = 1:lenSNR
    iSNR
    QamDEMOD = comm.RectangularQAMDemodulator('ModulationOrder',Mqam,...
        'BitOutput',true,'NormalizationMethod','Average power',...
        'AveragePower',SNR(iSNR),'DecisionMethod',...
        'Approximate log-likelihood ratio','VarianceSource','Property');
    
    for iSim = 1:Nsims
        
        NrFerror = 0;
        NrFerrorPy = 0;
        NrError = 0;
        NrErrorPy = 0;
        TotEstSNR = 0;
        Nblock = 0;
        
        while (NrFerror < MinFramError ) && (Nblock < MaxFramSimtd)
            
            Nblock = Nblock + 1;
            
            %Create Data and encode data
            Data = randi([0 1],Ninfo,1);
            Coded = LDPCENC(Data);
            Symbols = sqrt(SNR(iSNR)) * QAMMOD(Coded);
            
            %Transmit data -> Add noise
            Noise = sqrt(1/2) * ( randn(size(Symbols)) + 1i*randn(size(Symbols)));
            ChanOut = Symbols + Noise;
            TotEstSNR = TotEstSNR + mean(abs(Symbols).^2)/mean(abs(Noise).^2);
            
            %Decode Transmitted signal
            LLRs = QamDEMOD(ChanOut);
            Estimates = LDPCDEC(LLRs);
            %EstimatesPy = pyrunfile("Script.py", "message", parity=Hldpc, data=-LLRs);
            %EstimatesPy = double(EstimatesPy)';
            
            NrError = NrError + sum(xor(Estimates,Data));
            %NrErrorPy = NrErrorPy + sum(xor(EstimatesPy, Data)); 
            if sum(xor(Estimates,Data))>0
                NrFerror = NrFerror + 1;
            else    
            end
            %if sum(xor(EstimatesPy, Data))>0
            %    NrFerrorPy = NrFerrorPy + 1;
            %else
            %end
        end
        %ProbBerrPy(iSNR, iSim) = NrErrorPy /(Nblock * Ninfo)
        ProbBerr(iSNR,iSim) = NrError / (Nblock * Ninfo);
        
        ProbFerr(iSNR,iSim) = NrFerror / Nblock;
        %ProbFerrPy(iSNR, iSim) = NrFerrorPy/Nblock;
        AvgEstSNR(iSNR,iSim) =TotEstSNR / Nblock;
    end
end
%%
% if SNRdB and 10*log10(mean(AvgEstSNR,2)) do not agree, you're doing
% something wrong
figure(98);
grid on; hold on;
errorbar(SNRdB,mean(ProbBerr,2),std(ProbBerr,0,2),'blue-','linewidth',1);
errorbar(SNRdB,mean(ProbFerr,2),std(ProbFerr,0,2),'red-','linewidth',1);
%errorbar(SNRdB,mean(ProbBerrPy,2), std(ProbBerrPy,0,2), 'green-','linewidth',1)
%errorbar(SNRdB,mean(ProbFerrPy, 2), std(ProbFerrPy, 0, 2),'yellow-','linewidth',1)
xlim([min(SNRdB)-2 max(SNRdB)+2]);
set(gca,'YScale','log');