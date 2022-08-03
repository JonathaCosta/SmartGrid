#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jul  9 18:02:52 2022

@author: j
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de configuração do SHC de cada casa.
Retorno de chamadas do Módulo SCC.
"""
import ModLoad,ModTariff,ModConfFz,ModExecPSO

class SHC():
    '''
    Classe realiza a análise de consumo versus conforto aplicando agendamento de cargas
    via PSO com conforto Fuzzy.
    '''
    def __init__(self,sample_interval=5, tar=0, alfa=0, lst_cargas=0, 
                 conf_fz=0, graf=0, casa:int = 0):
        '''
        Método init carrega variável global :
            -'sample_interval=5'
            - tarifas
            - cargas
            - picos de cargas
        '''       
        ''' Variáveis'''
        self.alfa = alfa             # Carrega alfa da relação custo-conforto
        self.exibe_graf = graf       # Exibe gráfico
        self.casa = casa             # Identifica o número da casa para o gráfico
        self.iteracoes = 30 	  	     # Define o total de iterações para o PSO
        self.conf_fz = conf_fz       # Define se é conforto fuzzy ou no-fuzzy
        self.conf_alt = []		     # Armazena as variáveis linguísticas fuzzy 
        self.tab_cargas = lst_cargas # Identifica a tabela de cargas A,B ou C
            
        '''Módulo 01: tarifas e limite de pico de consumo para cargas não agendáveis'''
        if tar == 1: # set tarifa branca
            self.tarifa = ModTariff.Tariffs().Tariff_of_Use
        else:       # preset tarifa fixa
            self.tarifa = ModTariff.Tariffs().tariff_constant

        '''Módulo 02: Preenchimentos de objetos por amostragem com lista de cargas'''        
        if self.tab_cargas == 1: 
            self.cargas = ModLoad.DadosReferencia().cargas_lista1
            
        elif self.tab_cargas == 2: 
            self.cargas = ModLoad.DadosReferencia().cargas_lista2
        else:     
            self.cargas = ModLoad.DadosReferencia().cargas_lista3        
        
        '''Módulo 03: Conforto'''    
        self.Conforto_cargas()        

        '''Módulo 04:Valores de pico de carga por amostragem não agendáveis'''
        self.pico_cargas = ModLoad.Peak_ref().pico_cargas_nao_agendaveis
        
        '''Módulo 05: Execução do PSO'''
        self.Process_PSO()  
        
    def Conforto_cargas(self):
        '''
        Método recebe um objeto (carga) e atualiza o atributo (comfort level)
        em função de humor do usuário-admin, temperatura e umidade.
        Caso seja selecionada a opção de conforto fuzzy.
        Doutro modo utiliza valores default de temperatura, umidade,humor e omega
        Entrada: objeto comfortlevel_in
        Saída : objeto comfortlevel_out
        ''' 
        (t,u,h,omega) = ModConfFz.Fz_sim().Fuzificar()
        if self.conf_fz == 1:                # Utilizando conforto fuzzy      
            for i in (self.cargas):          # Altera o valor de relevância da carga                      
                if i.comfortLevel >= 0.5:                
                    i.comfortLevel = omega  
                    
        else:                               # Utilizando conforto não fuzzy
            (t,u,h,omega) = t,u,h,omega
                
                              
        self.conf_cargas_alt = t,u,h,round(omega,2),self.conf_fz

    def Process_PSO(self):
        '''
        Método de chamada para executar o PSO aplicando parametros do algoritmo e dos métodos sobre as cargas
        de modo que :
            * alfa [0,1] = [economia,conforto]
            * f = αf1 +(1−α)f2
        Para alfa = 0, o controlador obterá a melhor solução para os níveis de conforto do usuário conforme peso de alfa.
        Para alfa = 1, o controlador minimizará apenas os custos do consumo de eletricidade. De modo que haverá conforto, 
        pois as cargas serão acionadas, contudo esse não será um critério considerado pelo SHC para escolha dos horários.
        
        O método instancia o objeto 'sol' com os atributos da classe ExecPSO (dentro do módulo ModExecPSO). Seguidamente,
        é chamado o método que busca a melhor solução do PSO através de sol.PSO(), juntamente com as respostas
        gráficas para o referido valor de alfa.
        Isso é repetido para cada novo valor de alfa no laço 'for'.
        '''                                  
        sol = ModExecPSO.ExecPSO(alpha = self.alfa, 
                                 tarifa = self.tarifa,
                                 iteration=self.iteracoes,
                                 peak_limits= self.pico_cargas, 
                                 Loads = self.cargas,
                                 dados_fz  = self.conf_cargas_alt
                                )
        sol.PSO() 
        
        if self.exibe_graf == 1:
            sol.GrafAgendCargas(casa = self.casa, conf = self.conf_fz,
                                tab_cargas = self.tab_cargas)        
        self.casa_agend = sol.lst         
        
#******************************************************************************
# AREA DE TESTES
#******************************************************************************



