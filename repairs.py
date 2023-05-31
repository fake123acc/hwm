def OptScrap(cost, curr_dur, max_dur, rep_cost, verbose = False):
    """Get optimal cost per battle (cpb) for the given artifact.
    
    cost : int = price of the arifact
    curr_dur : int = current durability
    max_dur : int = maximum durability
    rep_cost : int = repair cost
    verbose : bool = wether you want to get detailed report via stoud
    
    returns (cpb, battles, total_cost, res)
    cbp : float = optimal cost per battle
    battles : int = total battles with optimal repair
    total_cost : int = cost of the artifact itself plus cost of all repairs
    res : list = list of SG levels used for each repair"""

 
    re = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9] # SG coefficient for each SG level respectively
    rc = [0.12,0.23,0.34,0.45,0.56,0.67,0.78,0.89,1.01] # smith repair cost multipleir for each SG level respectively
    
    res = []
    battles = curr_dur
    cpb = cost/battles if battles != 0 else 1e80
    d = max_dur

    while (d > 1):
        curr_cost = 0
        curr_battles = 0
        curr_i = None
        curr_cpb = cpb
        for i in range(9):
            if int(d*re[i]) == 0:
                continue
            if (cost+rep_cost*rc[i])/(battles+(int(d*re[i]))) < curr_cpb:
                curr_i = i
                curr_battles = int(d*re[i])
                curr_cost = round(rep_cost*rc[i])
                curr_cpb = (cost+rep_cost*rc[i])/(battles+(int(d*re[i])))
        if curr_i == None:
            break
        else:
            d -= 1
            cost += curr_cost
            battles += curr_battles
            cpb = cost/battles
            res += [curr_i]
            if verbose:
                print(f"repaired from 0/{d+1} to {curr_battles}/{d} for the {rc[curr_i]}, cpb is {cpb}")
    return cpb, battles, cost, res



def OptCost(cpb, curr_dur, max_dur, rep_cost):
    """Get artifact cost for the given durability and estimated cpb. 
    
    cpb : float = estimated cpb of the artifact
    curr_dur : int = current durability
    max_dur : int = maximum durability
    rep_cost : int = repair cost
    
    returns cost
    cost : int = maximum price which provides cpb lesser or equal than given if repaired optimally"""

    if OptScrap(0, curr_dur, max_dur, rep_cost)[0] > cpb:
        return 0
    
    def BinarySearchIteration (min_cost, max_cost, cpb, curr_dur, max_dur, rep_cost):
        middle = int((min_cost+max_cost)/2)
        if OptScrap(middle, curr_dur, max_dur, rep_cost)[0] > cpb:
            return min_cost, middle
        else:
            return middle, max_cost

    left = 0
    right = round(cpb*max_dur*max_dur/2)

    while right - left > 1:
        left, right = BinarySearchIteration(left, right, cpb, curr_dur, max_dur, rep_cost)
    return left


def OptSmith(cost, curr_dur, max_dur, rep_cost, smithing, verbose = False, cpb_m = 0):
    """Get artifact efficiency SG improwing wise. 
    
    cost : int = price of the arifact
    curr_dur : int = current durability
    max_dur : int = maximum durability
    rep_cost : int = repair cost
    smithing : float = current SG repair coefficient
    verbose : bool = wether you want to get detailed report via stoud
    cpb_m : float = estimated market cpb for this artifact. If zero, after-repair scrap counts as worth nothing. \
                    If non-zero, scrap is implied to be selled according to this cpb.
    
    returns (curr_eff, rep_count, rep_invest, battles)
    curr_eff : float = efficiency of SG imroving. Calculated as <gold for SG improving> / <gold wasted>
    rep_count : int = optimal number of repairs before disposal of artifact
    rep_invest : int = total gold spent on repairs
    battles : int = total battles until disposal
    """

    N = [curr_dur]
    i = max_dur
    while i > 1:
        N += [N[-1]+int(i*smithing)]
        i-=1

    eff = N.copy()
    cpb = OptScrap(cost, curr_dur, max_dur, rep_cost)[0]
    for i in range(len(N)): 
        eff[i] = rep_cost*i / (cost + rep_cost*i - cpb*N[i] - OptCost(cpb_m, 0, max_dur-i, rep_cost))


    curr_eff = 0
    curr_i = 0
    for i in range(len(N)):
        if curr_eff < eff[i]:
            curr_eff = eff[i]
            curr_i = i

    if verbose:
        print (f"repairing till 0/{max_dur - curr_i}, SG points gain is {rep_cost*curr_i/4000}, efficiency is {curr_eff} gold for the SG per 1 gold wasted. \n\
        Total cost is {cost + rep_cost*curr_i} with {N[curr_i]} battles gained (cpb {cpb})")
    return curr_eff, curr_i, rep_cost*curr_i, N[curr_i]


#### little nice table-drawing OptSmith wrapper ####

def OptSmithFancyOutput(price, c_d, m_d, r_c, cpb):
    """Draws table for each SG level.

    price : int = artifact cost
    c_d : int = current durability
    m_d : int = max durability
    r_c : int = repair cost
    cpb : float = estimated market cost per battle. If 0, scrap considered being thrown away. Otherwise its considered being selled

    returns nothing
    """

    import pandas as pd
    d = {'SG': [i for i in range(9)], '1pt cost': [0]*9, 'SG pts gain': [0]*9, 'gold spent': [0]*9, 'repaired up to': [0]*9, 'scrap cost': [0]*9, 'battles': [0]*9}
    df = pd.DataFrame(data=d)
    df.set_index('SG')

    for i in range(9): 
        res = OptSmith(price, c_d, m_d, r_c, i/10+0.1, False, cpb)
        df.at[i,'1pt cost'] = round(4000/res[0],2)
        df.at[i,'SG pts gain'] = round(res[2]/4000,2)
        df.at[i,'gold spent'] = res[2]+price
        df.at[i,'repaired up to'] = f"0/{m_d-res[1]}"
        df.at[i,'scrap cost'] = OptCost(cpb, 0, m_d-res[1], r_c)
        df.at[i,'battles'] = res[3]
    print(df.to_markdown())
    print("\n\n\n")



#### Tests for OptScrap ####

print(OptScrap(75000, 22, 50, 10000, True)) # test 1: cpb 372.70, 751 battles
print(OptScrap(75000, 0, 50, 10000, True)) # test 2: cpb 383.95, 729 battles
OptScrap(12989, 85, 85, 10469, True) # testcase from https://www.heroeswm.ru/forum_messages.php?tid=372095&page=10907#53653832
print("\n\n-------------------------------------------------------------\n\n")

#### Tests for OptCost ####

print(OptCost(152.69,85,85,10469)) # test 1: if it works?
print(OptScrap(OptCost(152.69,85,85,10469), 85,85,10469)) # test 2: res should be <= 152.69
print("\n\n-------------------------------------------------------------\n\n")

#### Tests for OptSmith ####

print(OptSmith(75000, 22, 50, 10000, 0.4, True)) # test1: 385k paid, 77.5 SG points earned, 444 battles gained with cpb 372.7 refund
print("\n\n-------------------------------------------------------------\n\n")

OptSmithFancyOutput(12989,85,85,10469,0) # test 2 : published at https://www.heroeswm.ru/forum_messages.php?tid=372095&page=10908#53654400

print("\n\n")

OptSmithFancyOutput(12989,85,85,10469,150) # test 3 : published at https://www.heroeswm.ru/forum_messages.php?tid=372095&page=10908#53654635
    

    
   