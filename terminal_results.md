@Kabir08 ➜ /workspaces/cot-hurts-performance (main) $ python evaluate_results.py
[OK] Scored results written to scored_results.csv

=== Accuracy by Model × Prompt Type ===
                                           model  prompt_type   correct
0                           llama-3.1-8b-instant  concise_cot  0.054167
1                           llama-3.1-8b-instant          cot  0.008333
2                           llama-3.1-8b-instant       direct  0.654167
3                        llama-3.3-70b-versatile  concise_cot  0.083333
4                        llama-3.3-70b-versatile          cot  0.066667
5                        llama-3.3-70b-versatile       direct  0.795833
6  meta-llama/llama-4-maverick-17b-128e-instruct  concise_cot  0.062500
7  meta-llama/llama-4-maverick-17b-128e-instruct          cot  0.012500
8  meta-llama/llama-4-maverick-17b-128e-instruct       direct  0.600000
9                                          model  prompt_type  0.000000

=== Accuracy by Model × Task ===
                                            model            task   correct
0                            llama-3.1-8b-instant      arithmetic  0.250000
1                            llama-3.1-8b-instant         factual  0.272222
2                            llama-3.1-8b-instant       reasoning  0.244444
3                            llama-3.1-8b-instant  symbolic_logic  0.188889
4                         llama-3.3-70b-versatile      arithmetic  0.300000
5                         llama-3.3-70b-versatile         factual  0.311111
6                         llama-3.3-70b-versatile       reasoning  0.383333
7                         llama-3.3-70b-versatile  symbolic_logic  0.266667
8   meta-llama/llama-4-maverick-17b-128e-instruct      arithmetic  0.250000
9   meta-llama/llama-4-maverick-17b-128e-instruct         factual  0.250000
10  meta-llama/llama-4-maverick-17b-128e-instruct       reasoning  0.255556
11  meta-llama/llama-4-maverick-17b-128e-instruct  symbolic_logic  0.144444
12                                          model            task  0.000000

=== CoT − Direct Accuracy Delta ===
prompt_type                                    cot_minus_direct
model                                                          
llama-3.1-8b-instant                                  -0.645833
llama-3.3-70b-versatile                               -0.729167
meta-llama/llama-4-maverick-17b-128e-instruct         -0.587500
model                                                       NaN
/workspaces/cot-hurts-performance/evaluate_results.py:102: SettingWithCopyWarning: 
A value is trying to be set on a copy of a slice from a DataFrame.
Try using .loc[row_indexer,col_indexer] = value instead

See the caveats in the documentation: https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html#returning-a-view-versus-a-copy
  subset["difficulty"] = pd.Categorical(
[OK] Saved figures/accuracy_vs_difficulty.png
[OK] Saved figures/accuracy_by_task.png
[OK] Saved figures/cot_failure_examples.csv

=== DONE: Evaluation Complete ===
@Kabir08 ➜ /workspaces/cot-hurts-performance (main) $ 