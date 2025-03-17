import pandas as pd

# Read tsv files into DataFrame
#------------------------------------------------------------------------------------------
# # df_edges = pd.read_csv('sample_edges.tsv', delimiter='\t')
df_edges = pd.read_csv('edges.tsv', delimiter='\t')
df_nodes = pd.read_csv('sample_nodes.tsv', delimiter='\t')

# test code to split edges data frame by metaedge column value
#------------------------------------------------------------------------------------------
# df_set_e_test = df_edges.groupby('metaedge')
# print(len(df_set_e_test))
# for ss in df_set_e_test:
#    print(ss)

# extract required edges from the full data frame
#------------------------------------------------------------------------------------------
df_cug = df_edges[df_edges['metaedge'] == 'CuG']
df_cdg = df_edges[df_edges['metaedge'] == 'CdG']
df_aug = df_edges[df_edges['metaedge'] == 'AuG']
df_adg = df_edges[df_edges['metaedge'] == 'AdG']
df_ctd = df_edges[df_edges['metaedge'] == 'CpD']
df_cpd = df_edges[df_edges['metaedge'] == 'CtD']
df_drd = df_edges[df_edges['metaedge'] == 'DrD']
df_dla = df_edges[df_edges['metaedge'] == 'DlA']
df_dug = df_edges[df_edges['metaedge'] == 'DuG']
df_ddg = df_edges[df_edges['metaedge'] == 'DdG']
df_dag = df_edges[df_edges['metaedge'] == 'DaG']

# merge (join) CuG and AdG
#------------------------------------------------------------------------------------------
df_cug_and_adg = pd.merge(df_cug, df_adg, suffixes=('_left', '_right'), on='target', how='inner')
# print(df_cug_and_adg)

# merge (join) CuG and AdG and DlA
#------------------------------------------------------------------------------------------
df_cug_and_adg_and_dla = pd.merge(df_dla, df_cug_and_adg, left_on='target', right_on='source_right', how='inner')
# print(len(df_cug_and_adg_and_dla))

# merge (join) CdG and AuG
#------------------------------------------------------------------------------------------
df_cdg_and_aug = pd.merge(df_cdg, df_aug, suffixes=('_left', '_right'), on='target', how='inner')
# print(df_cdg_and_aug)

# merge (join) CdG and AuG and DlA
#------------------------------------------------------------------------------------------
df_cdg_and_aug_and_dla = pd.merge(df_dla, df_cdg_and_aug, left_on='target', right_on='source_right', how='inner')
# print(len(df_cdg_and_aug_and_dla))

# concat (union) <CuG and AdG and DlA> and <CdG and AuG and DlA>
#------------------------------------------------------------------------------------------
df_compound_can_treat_a_disease = pd.concat([df_cug_and_adg_and_dla, df_cdg_and_aug_and_dla], axis=0)
# print(df_compound_can_treat_a_disease)
#print(len(df_compound_can_treat_a_disease))

# concat (union) <CuG and AdG and DlA> and <CdG and AuG and DlA>
#------------------------------------------------------------------------------------------
df_unique_compounds_has_treat = df_compound_can_treat_a_disease['source_left'].drop_duplicates()
#print(len(df_unique_compounds_has_treat))
# print(df_unique_compounds_has_treat)

# concat (union) CtD and CpD --> compounds which have edge to Disease
#------------------------------------------------------------------------------------------
df_compound_with_disease = pd.concat([df_ctd, df_cpd], axis=0)
#print(len(df_compound_with_disease))
# df_compound_with_disease_temp = df_compound_with_disease['source'].unique()
# print(len(df_compound_with_disease_temp))

# merge (join) <Compounds which have treat> and <Compounds which have disease>
#------------------------------------------------------------------------------------------
df_compound_old = pd.merge(df_unique_compounds_has_treat, df_compound_with_disease, left_on='source_left', right_on='source', how='left')
# print(len(df_compound_old))

# get the count of Compound (treat) but no link to disease
compound_old_result = df_compound_old['source'].drop_duplicates()
# print(len(compound_old_result))
# print(compound_old_result)

compound_old_result_list = list(compound_old_result)
compound_all_result_list = list(df_unique_compounds_has_treat)
compound_new_result_list = list(set(df_unique_compounds_has_treat) - set(compound_old_result))


print(compound_all_result_list)
print('----------------------------')
print(compound_new_result_list)
print('----------------------------')
print(compound_old_result_list)

# df_new_all = pd.DataFrame(df_unique_compounds_has_treat)
# df_old_all = pd.DataFrame(df_compound_old)
# df_new_result = pd.DataFrame(compound_new_result)

