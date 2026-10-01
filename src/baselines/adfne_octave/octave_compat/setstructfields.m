function s = setstructfields(s, snew)
% Octave compatibility shim for MATLAB's setstructfields.
% Copies every field of snew into s, overwriting existing fields.
% ADFNE source is NOT modified; this file simply supplies a function that
% ships with MATLAB but not with Octave.
  if isempty(snew); return; end
  fn = fieldnames(snew);
  for i = 1:numel(fn)
    s.(fn{i}) = snew.(fn{i});
  end
end
