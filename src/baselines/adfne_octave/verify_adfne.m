% Reproduces a documented ADFNE example before any project data is used.
run(fullfile(fileparts(mfilename('fullpath')),'adfne_init.m'));
L = Field(DFN('dim',2,'n',50),'Line');
printf('2D example : %d lines\n', size(L,1));
P = Field(DFN('dim',3,'n',30),'Poly');
printf('3D example : %d polygons, first has %d vertices\n', numel(P), size(P{1},1));
c = cell2mat(cellfun(@(q) mean(q,1), P, 'UniformOutput', false));
printf('3D centres lie in x[%.2f %.2f] y[%.2f %.2f] z[%.2f %.2f]\n', ...
   min(c(:,1)),max(c(:,1)),min(c(:,2)),max(c(:,2)),min(c(:,3)),max(c(:,3)));
printf('VERIFY OK\n');
