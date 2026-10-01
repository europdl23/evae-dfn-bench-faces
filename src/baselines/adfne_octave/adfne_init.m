% Bootstrap ADFNE 1.5 under GNU Octave. Run this first in every ADFNE session.
% ADFNE source is unmodified; octave_compat/ supplies functions Octave lacks.
pkg load statistics                      % ADFNE needs expcdf, expinv, etc.
here = fileparts(mfilename('fullpath'));
addpath(fullfile(here,'octave_compat')); % shims first, so they are found
addpath(fullfile(here,'ADFNE1.5'));
warning('off','all');
Globals;
global Report
Report = false;                          % set true for ADFNE's own progress output
printf('ADFNE 1.5 ready under Octave %s\n', version());
