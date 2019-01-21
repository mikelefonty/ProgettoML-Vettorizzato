from Utilities.UtilityCM import *
from MLP.MLP import *
from MLP.Activation_Functions import *

def f2phi(eta,mlp,X,T,gradE_h,gradE_o,lambd):

    #PESI ATTUALI
    W_h_current = mlp.W_h
    W_o_current = mlp.W_o

    #print("W_h",W_h_current)
    #print("W_o",W_o_current)

    #SPOSTO I PESI LUNGO DELTA_W ( = - GRADIENTE)
    mlp.W_h = mlp.W_h - (eta * gradE_h)
    mlp.W_o = mlp.W_o - (eta * gradE_o)

    #CALCOLO E(w + alpha* delta_W)
    phi_eta = compute_obj_function(mlp,X,T,lambd)

    # GRADIENTE CALCOLATO NEL NUOVO PUNTO
    gradE_h_new, gradE_o_new = compute_gradient(mlp,X,T,lambd)

    #METTO I GRADIENTI SOTTO FORMA DI VETTORE PER POTER FARE IL PRODOTTO SCALARE

    gradE_vec = matrix2vec(gradE_h,gradE_o)
    gradE_new_vec = matrix2vec(gradE_h_new,gradE_o_new)

    phi_p_eta = float(np.dot(gradE_new_vec.T, -gradE_vec))


    #RIMETTO I PESI COME ERANO ALL'INIZIO DELLA FUNZIONE
    mlp.W_h = W_h_current
    mlp.W_o = W_o_current

    #print("W_h dopo phi", mlp.W_h)
    #print("W_o dopo phi", mlp.W_o)

    return phi_eta, phi_p_eta

"""
Controlla se la condizione di armijio è soddisfatta
"""
def check_armijio(phi_zero,phi_prime_zero,phi_alpha,m1,alpha):

    assert m1 < 1
    assert m1 > 0

    return phi_alpha <= (phi_zero + m1*alpha*phi_prime_zero)

"""
Controlla se la condizione di strong Wolfe è soddisfatta
"""
def check_strong_wolfe(phi_prime_alpha,phi_prime_zero,m2):

    assert m2 < 1
    assert m2 > 0

    return abs(phi_prime_alpha) <= -m2 * phi_prime_zero


def AWLS(mlp,X,T,phi_0,gradE_h,gradE_o,lambd,eta_start=1,eta_max=20,max_iter=100,m1=0.001,m2=0.9,tau = 0.9,mina=1e-16,sfgrd = 0.001):

    assert eta_start > 0
    assert eta_max > eta_start
    assert lambd >= 0
    assert tau < 1
    assert max_iter > 0
    assert m1 > 0 and m1 < 1
    assert m2 > 0 and m2 > m1

    """
    Condizioni di arresto
    """
    done_max_iters = False
    reached_eta_max = False
    satisfied_arm_wolfe = False
    done_interpolation = False

    gradE_vec = matrix2vec(gradE_h, gradE_o)
    phi_p_0 = -(np.linalg.norm(gradE_vec) ** 2)  # phi'(0)

    """
    Mi servono per mantenere informazioni sulle iterate durante lo svolgimento dell'algoritmo
    """
    eta_prec = 0  #metto eta_0 = 0
    phi_eta_prec = phi_0 #phi(eta_0) = phi(0)
    phi_p_eta_prec = phi_p_0

    eta = eta_start
    eta_star = eta_start

    it = 0

    while (not done_max_iters) and (not reached_eta_max) and (not satisfied_arm_wolfe) and (not done_interpolation):


        phi_eta, phi_p_eta = f2phi(eta,mlp,X,T,gradE_h,gradE_o,lambd)
        print("[AWLS] Iterazione %s) Eta = %3f Eta_Max = %3f Phi(eta) =%s Phi'(eta)=%s"%(it +1,eta,eta_max,phi_eta,phi_p_eta))

        if (not check_armijio(phi_0,phi_p_0,phi_p_eta,m1,eta)) or (phi_eta >= phi_eta_prec):

            eta_star = zoom(mlp,X,T,gradE_h,gradE_o,lambd,eta_prec,eta,phi_eta_prec,phi_eta,phi_p_eta_prec,phi_p_eta,
                            phi_0,phi_p_0,m1,m2,max_iter,mina,sfgrd)
            done_interpolation = True

        elif check_strong_wolfe(phi_p_eta,phi_p_0,m2):

            eta_star = eta
            satisfied_arm_wolfe = True

        elif phi_p_eta >= 0:
            eta_star = zoom(mlp,X,T,gradE_h,gradE_o,lambd,eta,eta_prec,phi_eta,phi_eta_prec,phi_p_eta,phi_p_eta_prec,
                            phi_0,phi_p_0,m1,m2,max_iter,mina,sfgrd)
            done_interpolation = True

        else:

            """
            Aggiorno eta ed eta_prec
            """
            tmp = eta
            eta = eta / tau
            eta_prec = tmp
            phi_eta_prec = phi_eta
            phi_p_eta_prec = phi_p_eta


            if eta > eta_max:
                reached_eta_max = True
                eta_star = eta_max

            it += 1
            if it >= max_iter:
                done_max_iters = True
                eta_star = eta

    if done_max_iters:
        print("Raggiunto il numero massimo di iterazioni")
    elif done_interpolation:
        print("Effettuata interpolazione")
    elif reached_eta_max:
        print("Raggiunto eta massimo")
    elif satisfied_arm_wolfe:
        print("Soddisfatte le condizioni di Armijo-Wolfe")
    return eta_star


def zoom(mlp,X,T,gradE_h,gradE_o,lambd,eta_l,eta_h,phi_eta_l,phi_eta_h,phi_p_eta_l,phi_p_eta_h,phi_0,phi_p_0,m1,m2,
         max_iters,mina,sfgrd):

    #print("ENTRO IN ZOOM")
    eta_low = eta_l
    eta_high = eta_h
    phi_eta_low = phi_eta_l
    phi_eta_high = phi_eta_h
    phi_p_eta_low = phi_p_eta_l
    phi_p_eta_high = phi_p_eta_h

    eta_star = eta_low

    satisfied_aw =False
    done_max_iters = False
    too_close = False

    it = 0
    while (not satisfied_aw) and (not done_max_iters) and (not too_close):


        print("[ZOOM] Iterazione %s) Faccio interpolazione in [%s,%s]"%(it+1,eta_low,eta_high))

        if abs(eta_high - eta_low) <= mina:
            eta_star = eta_low
            too_close = True

        else:
            eta = ( (eta_low * phi_p_eta_high) - (eta_high * phi_p_eta_low)) / (phi_p_eta_high - phi_p_eta_low)
            eta = max([min([eta_low,eta_high]) * (1 + sfgrd), min([max([eta_low,eta_high]) * (1 - sfgrd), eta])])

            print("[ZOOM] Eta interpolato = ",eta)

            phi_eta, phi_p_eta = f2phi(eta,mlp,X,T,gradE_h,gradE_o,lambd)

            if (not check_armijio(phi_0,phi_p_0,phi_eta,m1,eta)) or (phi_eta >= phi_eta_low):
                eta_high = eta
                phi_eta_high = phi_eta
                phi_p_eta_high = phi_p_eta

            else:

                if check_strong_wolfe(phi_p_eta,phi_p_0,m2):
                    eta_star = eta
                    satisfied_aw = True

                elif phi_p_eta * (eta_high - eta_low) >= 0:
                    eta_high = eta_low
                    phi_eta_high = phi_eta_low
                    phi_p_eta_high = phi_p_eta_low

                eta_low = eta
                phi_eta_low = phi_eta
                phi_p_eta_low = phi_p_eta

            it += 1

            if it >= max_iters:
                done_max_iters = True
                eta_star = eta

    if too_close:
        print("[ZOOM] Terminato per intervallo troppo piccolo")

    elif done_max_iters:
        print("[ZOOM] Terminato il numero massimo di iterazioni")

    elif satisfied_aw:
        print("[ZOOM] Soddisfatte AW")

    print("[ZOOM] Eta restituito = ",eta_star)

    return eta_star




