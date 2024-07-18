'''
RTM - Rede de Telecomunicações para o Mercado

Direitos de Uso e auteração conforme necessidade a RTM.

Esse script foi criado para suprir uma necessidade de monitorar as VRFs com o mesmo IP de Neighbor 
que por limitação do SNMP não é possível ter o status de todas elas.

Autor: Marcio da Silva Padilha de Oliveira
Colaboradores: Edson Monteiro de Almeida e Igor Lopes da Silva
Coordenadores: Evandro Alves de Souza e João Vitor Longo Salvioni


Agradecimentos:
Permite realizar todos os testes em uma unica sessão:
https://community.cisco.com/t5/call-control/unable-to-execute-second-python-interact-send-command-in-my/td-p/4913623
Marcel Zehnder e @mradell 
'''
from netmiko import ConnectHandler
#import logging
import time
import datetime

'''
def getips(x):
    IPs=[]
    for i in x:  
        if not x in IPs:
            IPs.append(i)
    return IPs
cont = 0
'''
#logging.basicConfig(filename='netmiko.log', level=logging.DEBUG)
#logger = logging.getLogger("netmiko")
#username 0rion pri 1 sec BgP#teste@

device = [{
        "device_type": "generic",
        "ip": "ip",
        "username": "user",
        "password": "pass",
        "prompt": "R1#*"
},
        {
        "device_type": "generic",
        "ip": "ip",
        "username": "user",
        "password": "pass",
        "prompt": "R2#*"
}]

html_head = ["<!DOCTYPE html>","<html>","<body>","<style>","p","{","margin:0;","padding:0;","font-size:15px;","line-height:15px;","}","table, tr","{","border:1px solid black;","border-collapse: collapse;","}","td","{","text-align:center;","}""</style>"]
lastlist = []

while True:
    with open('resultado.html','w') as arquivo:
        grafana = open('grafana.txt','w')
        for txt in html_head:
            arquivo.write(txt+'\n')
        try:
            thisresult=[]
            for i in range(len(device)):
                cmd1 = "sh ip bgp vpnv4 all sum | i Idle|Active"
                LIST1=[]
                SCAN1 = []
                RESULTADO={}
                router = {"device_type": device[i].get("device_type"),"ip": device[i].get("ip"),"username": device[i].get("username"),"password": device[i].get("password")}
                with ConnectHandler(**router) as ssh:

                    prompt = device[i].get("prompt")
                    '''
                    commands = [
                        cmd1,
                        cmd2,
                        cmd3
                    ]
                    '''
                    time.sleep(1)

                    output1 = ssh.send_command(cmd1, expect_string=prompt)
                    #print(f"=== {cmd1} ===")
                    
                    SCAN1 = output1.splitlines()
                    #print(SCAN1)
                    for SCAN1_ in SCAN1:
                        temp1 = SCAN1_.split()
                        LIST1.append(temp1[0]) if not temp1[0] in LIST1 else None
                

                    
                    for ip1 in LIST1:
                        output2 = ssh.send_command("sh ip bgp vpnv4 all nei "+ str(ip1) + " | i vrf", expect_string=prompt)
                        SCAN2 = output2.splitlines()
                        #print(SCAN2)
                        output3 = ssh.send_command("sh ip bgp vpnv4 all sum | i "+ str(ip1), expect_string=prompt)
                        SCAN3 = output3.splitlines()
                        DIC2={}
                        for i in range(len(SCAN2)):
                            temp2 = SCAN2[i].split()
                            DIC2.update({i:(temp2[3][:-1],temp2[5][:-1],temp2[8][:-1])})

                        DIC3={}
                        for i in range(len(SCAN3)):
                            temp3 = SCAN3[i].split()
                            DIC3.update({i:(temp3[0],temp3[-1],temp3[-2])})

                        for i in range(len(DIC2)):
                            if DIC3.get(i)[1] == 'Active' or DIC3.get(i)[1] == '(Admin)' or DIC3.get(i)[1] == 'Idle':
                                RESULTADO.update({len(RESULTADO):(DIC2.get(i)[1], DIC2.get(i)[2], DIC2.get(i)[0], DIC3.get(i)[1], DIC3.get(i)[2])})
                        #--------------------------------------------------------------------------------------------------------------------------
                #print(f"=== {prompt.replace("#*","")} ===")
                #grafana.write(f'#{prompt.replace("#*","")}\n')
                arquivo.write(f'<p>=== {prompt.replace("#*","")} Total: {len(RESULTADO)} ===</p>\n')
                arquivo.write('<br>\n')
                arquivo.write(f'<p><table><tr><th>VRF</th><th style="width: 12px"> </th><th>AS</th><th> </th><th>IP do neighbor</th><th> </th><th>Status</th><th> </th><th>Tempo</th></tr>\n')
                for i in range(len(RESULTADO)):
                    #print(f"A VRF {RESULTADO.get(i)[0]} do AS {RESULTADO.get(i)[1]}, IP do Nieghbor {RESULTADO.get(i)[2]} esta com status {RESULTADO.get(i)[3] if RESULTADO.get(i)[3] != '(Admin)' else 'Shutdown'}")
                    #arquivo.write(f"<p>A VRF {RESULTADO.get(i)[0]} do AS {RESULTADO.get(i)[1]}, IP do Nieghbor {RESULTADO.get(i)[2]} esta com status {RESULTADO.get(i)[3] if RESULTADO.get(i)[3] != '(Admin)' else 'Shutdown'} desde {RESULTADO.get(i)[4]}</p>\n")
                    listresult = 'BGP_Cloudlink{router="'+prompt.replace("#*","")+'",VRF="'+RESULTADO.get(i)[0]+'",AS="'+RESULTADO.get(i)[1]+'",IP_Neighbor="'+RESULTADO.get(i)[2]+'}' #+ ' Down' if RESULTADO.get(i)[3] != '(Admin)' else ' Shutdown'
                    thisresult.append(listresult + ' Down' if RESULTADO.get(i)[3] != '(Admin)' else ' Shutdown')
                    if i % 2 == 0:
                        arquivo.write(f'<p><tr style="background-color: lightgray"><td>{RESULTADO.get(i)[0]}</td><th style="width: 12px"> </th><td>{RESULTADO.get(i)[1]}</td><th style="width: 12px"> </th><td>{RESULTADO.get(i)[2]}</td><th style="width: 12px"> </th><td>{RESULTADO.get(i)[3] if RESULTADO.get(i)[3] != '(Admin)' else 'Shutdown'}</td><th style="width: 12px"> </th><td>{RESULTADO.get(i)[4]}</td></tr></p>\n')
                    else:
                        arquivo.write(f'<p><tr><td>{RESULTADO.get(i)[0]}</td><th style="width: 12px"> </th><td>{RESULTADO.get(i)[1]}</td><th style="width: 12px"> </th><td>{RESULTADO.get(i)[2]}</td><th style="width: 12px"> </th><td>{RESULTADO.get(i)[3] if RESULTADO.get(i)[3] != '(Admin)' else 'Shutdown'}</td><th style="width: 12px"> </th><td>{RESULTADO.get(i)[4]}</td></tr></p>\n')
                arquivo.write('</table>\n')
                arquivo.write('<br>\n')
            arquivo.write(f'<p>=== Atualizada em: {datetime.datetime.now().strftime("%d/%m/%Y %H:%M")} ===</p>\n')
            arquivo.write('</body>\n')
            arquivo.write('</html>')
            arquivo.close()

            
            if lastlist == []:
                lastlist = thisresult
                for wgrafana in thisresult:
                    grafana.write(wgrafana + '\n')
            else:
                TempList1=[]
                TempList2=[]
                for TList1 in thisresult: #12
                    TempList1.append(str(TList1).split(' '))
                for TList2 in lastlist: #11
                    TempList2.append(str(TList2).split(' '))
                lastlist = []
                for check1,check2 in TempList1:
                    count = 0
                    total = len(TempList2)
                    for x,y in TempList2:
                        if check1 == x:
                            grafana.write(str(x) + ' ' + str(check2) + '\n')
                            lastlist.append(str(x) + ' ' + str(check2))
                        else:
                            count += 1
                            if count == total:
                                grafana.write(str(check1) + ' ' + str(check2) + '\n')
                                lastlist.append(str(check1) + ' ' + str(check2))
                for check1,check2 in TempList2:
                    count = 0
                    total = len(TempList1)
                    for x,y in TempList1:
                        if check1 == x:
                            None
                        else:
                            count += 1
                            if count == total:
                                if check2 != "Up":
                                    grafana.write(str(check1)+ ' Up\n')
                                    lastlist.append(str(check1) + ' Up')

            print(lastlist)          
            grafana.close()
            time.sleep(120)
            #break
        except:
            arquivo.write(f'<p>=== sem conexão ===</p>\n')
            arquivo.write('<br>\n')
            arquivo.write(f'<p>=== Atualizada em: {datetime.datetime.now().strftime("%d/%m/%Y %H:%M")} ===</p>\n')
            arquivo.write('</body>\n')
            arquivo.write('</html>')
            grafana.close()
            arquivo.close()
            time.sleep(120)
            #break           
