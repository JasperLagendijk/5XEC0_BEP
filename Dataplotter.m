%% Initial settings
clc, clear all, close all
% Extract data from CSV file0
fname1 = ["1_2_code_rate.csv", "2_3_code_rate.csv",  "3_4_code_rate.csv", "5_6_code_rate.csv"];
fname2 = ["attenuated_1_2.csv", "attenuated_2_3.csv", "attenuated_3_4.csv"];
SNRdB = 1:8;  
M = zeros(length(fname1),length(SNRdB), 5);
N = zeros(length(fname2), length(SNRdB), 10);


%% Load data 
for name = 1:length(fname1)
    % Load data
    [Type, Berr, EncR, SNR] = csvimport( convertStringsToChars(fname1(name)), 'columns', {'Type', 'Bit Error Rate', 'CodeRate', 'SNR'} );
    
    for i = 1:length(Berr)
    x = cell2mat(Type(i));
    if strcmp(x, 'gallager')
        M(name, SNR(i), 1) = Berr(i);
    elseif strcmp(x, 'min-sum')
        M(name, SNR(i), 2) = Berr(i);
    elseif strcmp(x, 'attenuated')
        M(name, SNR(i), 3) = Berr(i);
    %elseif strcmp(x, 'offset')
       %M(name, SNR(i), 4) = Berr(i);
    elseif strcmp(x, 'default')
        M(name, SNR(i), 5) = Berr(i);
    end
    end
end

for name = 1:length(fname2)
    [Type, Berr, EncR, SNR, factor] =  csvimport( convertStringsToChars(fname2(name)), 'columns', {'Type', 'Bit Error Rate', 'CodeRate', 'SNR', 'factor'} );
   for i = 1:length(Berr)
        N(name, SNR(i), 10*factor(i)) = Berr(i);
   end
end

% Simulated data from matlab decoder
ProbBerr = [0.261049382716049, 0.236141975308642, 0.205586419753086, 0.181358024691358, 0.136975308641975, 0.062158623269734, 0.002974142873524, 0;
                    0.265185185185185, 0.238518518518519, 0.208125000000000, 0.185949074074074, 0.165277777777778, 0.140925925925926, 0.110578703703704, 0.0730759429153925;
                    0.264362139917695, 0.237695473251029, 0.211316872427984, 0.186646090534979, 0.164773662551440, 0.140843621399177, 0.117880658436214, 0.0920576131687243;
                    0.261000000000000, 0.239259259259259, 0.212370370370370, 0.187629629629630, 0.163055555555556, 0.142500000000000, 0.121055555555556, 0.0972592592592593];

%ProbBerr = [0.261049382716049, 0.236141975308642, 0.205586419753086, 0.181358024691358, 0.137345679012346, 0.0653594771241830, 0.00414359691089251, 4.32098765432099e-06];


%% Plot
close all
p_name1 = ["1/2 Rate Encoded", "2/3 Rate Encoded", "3/4 Rate Encoded", "5/6 Encoded"];
p_name2 = ["1/2 Rate Attenuated", "2/3 Rate Attenuated", "3/4 Rate Attenuated", "5/6 Attenuated"];


close all
for name = 1:length(fname1)
    figure(name)
    %subplot(2, 2, name)
    hold on
    grid on
    plot(squeeze(M(name, :, :)))
    plot(squeeze(ProbBerr(name, :)))
    set(gca,'YScale','log');
    set(gca, 'ColorOrder',  linspecer(length(squeeze(M(name, 1, :)))));
    lgd = legend('gallager', 'min-sum', 'attenuated', 'offset', 'checknode', 'matlab');
    title(p_name1(name))
    hold off
end

for name = 1:length(fname2)
    figure(name+length(fname1))
    hold on
    grid on
    plot(SNRdB, squeeze(N(name, :, :)))
   
    set(gca, 'YScale', 'log')
    set(gca, 'ColorOrder',  linspecer(length(squeeze(N(name, 1, :)))));
    lgd = legend('0.1', '0.2', '0.3', '0.4', '0.5', '0.6', '0.7', '0.8', '0.9', '1')
    title(p_name2(name))
    hold off
end
