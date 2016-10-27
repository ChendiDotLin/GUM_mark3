__author__ = 'brian'
import numpy as np
import matplotlib.pyplot as plt
import mc_supercell as mcs
from copy import deepcopy
from mpl_toolkits.mplot3d import Axes3D


def eval_site(site,supercell_obj,BEG_rules,Cluster_rules,J_rules,Js,T):
        Kb = .000086173324
        Ham = 0
        Ham_BEG = 0
        Ham_Clust = 0
        Ham_Spin = 0
        for i in range(supercell_obj.get_number_of_neighbors(site)):
            BEG_J = 0
            BEG_K = 0
            for j in range(len(BEG_rules)):
                if supercell_obj.get_composition() == BEG_rules[j].composition:
                    if supercell_obj.get_neighbor_order(site,i) == BEG_rules[j].neighbor_order:
                       if supercell_obj.get_neighbor_plain(site,i) == BEG_rules[j].plane or BEG_rules[j].plane == 'ALL':
                            if supercell_obj.get_site_species(site) in BEG_rules[j].home_atom_list:
                                if supercell_obj.get_neighbor_species(site,i) in BEG_rules[j].neighbor_atom_list:
                                    if BEG_rules[j].phase == 'mart':
                                        BEG_J = float(Js[j])
                                    if BEG_rules[j].phase == 'aust':
                                        BEG_K = float(Js[j])
            home_phase = supercell_obj.get_site_phase(site)
            neighbor_phase = supercell_obj.get_neighbor_phase(site,i)
            #Ham += -BEG_J*home_phase*neighbor_phase-BEG_K*(home_phase**2)*(neighbor_phase**2)+6*BEG_K*home_phase**2-6*supercell_obj.num_sites*BEG_K/2
            Ham += -(BEG_J*home_phase*neighbor_phase+BEG_K*(1-home_phase**2)*(1-neighbor_phase**2)) #- Kb*T*np.log(2)*(1-supercell_obj.get_site_spin(site)**2)
            Ham_BEG += -(BEG_J*home_phase*neighbor_phase+BEG_K*(1-home_phase**2)*(1-neighbor_phase**2)) - Kb*T*np.log(2)*(1-supercell_obj.get_site_spin(site)**2)

            # for j in range(len(Cluster_rules)):
            #     if supercell_obj.get_neighbor_order(site,i) == Cluster_rules[j].neighbor_order:
            #         if supercell_obj.get_neighbor_plain(site,i) == Cluster_rules[j].plane or Cluster_rules[j].plane == 'ALL':
            #             if supercell_obj.check_site_phase(site) == Cluster_rules[j].phase:
            #                 if supercell_obj.get_site_species(site) in Cluster_rules[j].home_atom_list:
            #                     if supercell_obj.get_neighbor_species(site,i) in Cluster_rules[j].neighbor_atom_list:
            #                         if Cluster_rules[j].neighbor_arrangement == 'PERM':
            #                             if supercell_obj.get_site_species(site) != supercell_obj.get_neighbor_species(site,i):
            #                                 Ham += float(Js[j+len(BEG_rules)])
            #                                 Ham_Clust += float(Js[j+len(BEG_rules)])
            #                         if Cluster_rules[j].neighbor_arrangement == 'COMB':
            #                             Ham += float(Js[j+len(BEG_rules)])
            #                             Ham_Clust += float(Js[j+len(BEG_rules)])
            #
            #
            # for j in range(len(J_rules)):
            #     if supercell_obj.get_neighbor_order(site,i) == J_rules[j].neighbor_order:
            #         if supercell_obj.get_neighbor_plain(site,i) == J_rules[j].plane or J_rules[j].plane == 'ALL':
            #             if supercell_obj.check_site_phase(site) == J_rules[j].phase:
            #                 if supercell_obj.get_site_species(site) in J_rules[j].home_atom_list:
            #                     if supercell_obj.get_neighbor_species(site,i) in J_rules[j].neighbor_atom_list:
            #                         if J_rules[j].neighbor_arrangement == 'PERM':
            #                             if supercell_obj.get_site_species(site) != supercell_obj.get_neighbor_species(site,i):
            #                                 home_spin = supercell_obj.get_site_spin(site)
            #                                 neighbor_spin = supercell_obj.get_neighbor_spin(site,i)
            #                                 Ham += float(Js[j+len(BEG_rules)+len(Cluster_rules)])*home_spin*neighbor_spin
            #                                 Ham_Spin += float(Js[j+len(BEG_rules)+len(Cluster_rules)])*home_spin*neighbor_spin
            #                         if J_rules[j].neighbor_arrangement == 'COMB':
            #                             home_spin = supercell_obj.get_site_spin(site)
            #                             neighbor_spin = supercell_obj.get_neighbor_spin(site,i)
            #                             Ham += float(Js[j+len(BEG_rules)+len(Cluster_rules)])*home_spin*neighbor_spin
            #                             Ham_Spin += float(Js[j+len(BEG_rules)+len(Cluster_rules)])*home_spin*neighbor_spin
        #print([Ham_BEG,Ham_Clust,Ham_Spin])
        #print(Ham)
        return Ham

def eval_lattice(supercell_obj,BEG_rules,Cluster_rules,J_rules,Js,T,do_figs=True):
    total_Ham = 0
    total_phase = 0
    total_phase2 = 0
    total_spin = 0
    total_spin2 = 0
    for i in range(supercell_obj.i_length):
        for j in range(supercell_obj.j_length):
            for k in range(supercell_obj.k_length):
                site = [i,j,k]
                total_Ham += eval_site(site,supercell_obj,BEG_rules,Cluster_rules,J_rules,Js,T)
                total_phase += supercell_obj.get_site_phase(site)/supercell_obj.num_sites
                total_phase2 += supercell_obj.get_site_phase(site)**2/supercell_obj.num_sites
                total_spin += supercell_obj.get_site_spin(site)/supercell_obj.num_sites
                total_spin2 += supercell_obj.get_site_spin(site)**2/supercell_obj.num_sites
    return total_Ham,total_phase,total_phase2,total_spin,total_spin2

def flip_phase(site,supercell_obj):
    old_phase = supercell_obj.get_site_phase(site)
    phase_changed = False
    while phase_changed == False:
        rand = np.random.random()
        if rand <= 1/2.0:
            phase = 0
        elif rand > 1/2.0 and rand <= 3/4.0:
            phase = -1
        elif rand >3/4.0:
            phase = 1
        if phase != old_phase:
            phase_changed = True
    supercell_obj.set_site_phase(site,phase)
    return old_phase

def flip_species(site_1,site_2,supercell_obj):
    old_species_1 = supercell_obj.get_site_species(site_1)
    old_phase_1 = supercell_obj.get_site_phase(site_1)
    old_spin_1 = supercell_obj.ge_site_spin(site_1)
    old_state_1 = [old_species_1,old_phase_1,old_spin_1]

    old_species_2 = supercell_obj.get_site_species(site_2)
    old_phase_2 = supercell_obj.get_site_phase(site_2)
    old_spin_2 = supercell_obj.ge_site_spin(site_2)
    old_state_2 = [old_species_2,old_phase_2,old_spin_2]

    supercell_obj.set_site_species(site_1,old_species_2)
    supercell_obj.set_site_phase(site_1,old_phase_2)
    supercell_obj.set_site_spin(site_1,old_spin_2)
    supercell_obj.set_site_species(site_2,old_species_1)
    supercell_obj.set_site_phase(site_2,old_phase_1)
    supercell_obj.set_site_spin(site_2,old_spin_2)
    return old_state_1,old_state_2

def flip_spin(site,supercell_obj):
    old_spin = supercell_obj.get_site_spin(site)
    spin_changed = False
    while spin_changed == False:
        rand = np.random.random()
        if rand <= 1/2.0:
            spin = 0
        elif rand > 1/2.0 and rand <= 3/4.0:
            spin = -1
        elif rand >3/4.0:
            spin = 1
        if spin != old_spin:
            spin_changed = True
    supercell_obj.set_site_spin(site,spin)
    return old_spin

def run_montecarlo(supercell_obj,numb_passes,temp,BEG_rules,Cluster_rules,J_rules,Js,do_figs=True):
    T = temp
    Kb = .000086173324 #8.6173324(78)×10−5 eV*K^-1
    H_avg = 0
    mag_avg = 0
    mag2_avg = 0
    p_avg = 0
    p2_avg = 0
    inc = 0
    inc_not = 0
    H_total,p,p2,mag,mag2 = eval_lattice(supercell_obj,BEG_rules,Cluster_rules,J_rules,Js,T)
    for passes in range(numb_passes):
        for i in range(supercell_obj.i_length):
            for j in range(supercell_obj.j_length):
                for k in range(supercell_obj.k_length):
                    site = [i,j,k]

                    old_Ham = eval_site(site,supercell_obj,BEG_rules,Cluster_rules,J_rules,Js,T)
                    old_phase = flip_phase(site,supercell_obj)
                    new_Ham = eval_site(site,supercell_obj,BEG_rules,Cluster_rules,J_rules,Js,T)
                    if new_Ham > old_Ham:
                        rand = np.random.random()
                        prob = np.exp(-1/(Kb*T)*(new_Ham-old_Ham))
                        if rand > prob:
                            supercell_obj.set_site_phase(site,old_phase)
                            inc_not += 1
                        else:
                            H_total += new_Ham-old_Ham
                            inc += 1
                    else:
                        H_total += new_Ham-old_Ham
                        inc += 1
    #
    #                 if supercell_obj.get_site_species(site) != 0:
    #                     composition = supercell_obj.get_composition()
    #                     if composition[2] != 0:
    #                         site_found = False
    #                         while site_found == False:
    #                             site_2 = [np.random.randint(0,supercell_obj.i_length),np.random.randint(0,supercell_obj.j_length),np.random.randint(0,supercell_obj.k_length)]
    #                             if supercell_obj.get_site_species(site_2) != supercell_obj.get_site_species(site):
    #                                 if supercell_obj.get_site_species(site_2) != 0:
    #                                     site_found = True
    #                         old_Ham = eval_site(site,supercell_obj,BEG_rules,Cluster_rules,J_rules,Js)
    #                         old_Ham += eval_site(site_2,supercell_obj,BEG_rules,Cluster_rules,J_rules,Js)
    #                         old_site_state,old_site_2_state = flip_species(site,site_2,supercell_obj)
    #                         new_Ham = eval_site(site,supercell_obj,BEG_rules,Cluster_rules,J_rules,Js)
    #                         new_Ham += eval_site(site_2,supercell_obj,BEG_rules,Cluster_rules,J_rules,Js)
    #                         if new_Ham > old_Ham:
    #                             rand = np.random.random()
    #                             prob = np.exp(-1/(Kb*T)*(new_Ham-old_Ham))
    #                             if rand > prob:
    #                                 _old_species = old_site_state[0]
    #                                 _old_phase = old_site_state[1]
    #                                 _old_spin = old_site_state[2]
    #                                 supercell_obj.set_site_species(site,_old_species)
    #                                 supercell_obj.set_site_phase(site,_old_phase)
    #                                 supercell_obj.set_site_spin(site,_old_spin)
    #                                 _old_species2 = old_site_2_state[0]
    #                                 _old_phase2 = old_site_2_state[1]
    #                                 _old_spin2 = old_site_2_state[2]
    #                                 supercell_obj.set_site_species(site_2,_old_species2)
    #                                 supercell_obj.set_site_phase(site_2,_old_phase2)
    #                                 supercell_obj.set_site_spin(site_2,_old_spin2)
    #                                 inc_not += 1
    #                             else:
    #                                 H_total += new_Ham-old_Ham
    #                                 inc += 1
    #                         else:
    #                             H_total += new_Ham-old_Ham
    #                             inc += 1
    #
    #                 old_Ham = eval_site(site,supercell_obj,BEG_rules,Cluster_rules,J_rules,Js)
    #                 old_spin = flip_spin(site,supercell_obj)
    #                 new_Ham = eval_site(site,supercell_obj,BEG_rules,Cluster_rules,J_rules,Js)
    #                 if new_Ham > old_Ham:
    #                     rand = np.random.random()
    #                     prob = np.exp(-1/(Kb*T)*(new_Ham-old_Ham))
    #                     if rand > prob:
    #                         supercell_obj.set_site_spin(site,old_spin)
    #                         inc_not += 1
    #                     else:
    #                         H_total += new_Ham-old_Ham
    #                         inc += 1
    #                 else:
    #                     H_total += new_Ham-old_Ham
    #                     inc += 1

        H_total2,p,p2,mag,mag2 = eval_lattice(supercell_obj,BEG_rules,Cluster_rules,J_rules,Js,T)
        print([H_total,H_total2])
        # inc +=1
        # if inc >= 100:
        #     T -= 100
        #     inc = 0
        #     if T <= 0:
        #         T = 1
        #T -= 1
        #if T <= 0:
        #    T = 1
        #print(T)
        # inc += 1
        # if inc >= 100:
        #     inc = 0

        if passes >= numb_passes*.9:
            H_avg += H_total/(numb_passes*.1)
            mag_avg += mag/(numb_passes*.1)
            mag2_avg += mag2/(numb_passes*.1)
            p_avg += p/(numb_passes*.1)
            p2_avg += p2/(numb_passes*.1)

        plt.figure(2)
        #plt.plot(passes,H_total/supercell_obj.num_sites,lw=3,marker='o',color='b')
        plt.plot(passes,H_total,lw=3,marker='o',color='b')
        plt.figure(3)
        plt.subplot(311)
        plt.plot(passes,mag,lw=3,marker='o',color='g')
        plt.subplot(312)
        plt.plot(passes,mag2,lw=3,marker='o',color='g')
        plt.figure(4)
        plt.subplot(411)
        plt.plot(passes,p,lw=3,marker='o',color='r')
        plt.subplot(412)
        plt.plot(passes,p2,lw=3,marker='o',color='r')
    if do_figs is True:
        plt.figure(2)
        plt.savefig('Enrg.png')
        plt.figure(3)
        plt.savefig('Mag.png')
        plt.figure(4)
        plt.savefig('Phase.png')
    temp_output = open('Temp_data','a')
    temp_output.write(str(T)+'  '+str(H_avg/supercell_obj.num_sites)+'  '+str(mag_avg)+'  '+str(mag2_avg)+'  '+str(p_avg)+'  '+str(p2_avg)+'\n')
    temp_output.close()
    print(inc)
    print(inc_not)

    fig = plt.figure(5)
    ax = fig.add_subplot(111, projection='3d')
    xs = []
    ys = []
    zs = []
    cs = []
    us = []
    vs = []
    ws = []
    for i in range(supercell_obj.i_length):
        for j in range(supercell_obj.j_length):
            for k in range(supercell_obj.k_length):
                if np.mod(k,2) == 0:
                    offset = 0
                else:
                    offset = .5
                site = [i,j,k]
                pos = supercell_obj.get_site_pos(site)
                xs.append(pos[0]+offset)
                ys.append(pos[1]+offset)
                zs.append(pos[2]*.5)
                us.append(0)
                vs.append(0)
                ws.append(supercell_obj.get_site_spin(site))
                if supercell_obj.get_site_species(site) == 0:
                    cs.append('g')
                if supercell_obj.get_site_species(site) == 1:
                    cs.append('r')
                if supercell_obj.get_site_species(site) == 2:
                    cs.append('b')
    ax.quiver(xs,ys,zs,us,vs,ws,pivot='middle',length=.5)
    ax.scatter(xs,ys,zs,c=cs,marker='o',s=50)
    plt.savefig('3D_plt.png')

