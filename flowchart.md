flowchart TB
    Start(["CONDICIONES INICIALES"]) --> Init["T = 0; Δt = 1; TF = 60;<br>DIA_MES = 1; DIA_SEM = 1;<br>ST = 30000; IP = 0; FLL = ∞; COMPRA_MES = 0;<br>TP = 30000; PE = 5000; SS = 2500;<br>CALM = 126; C_UNIT_PED = 1150; C_UNIT_EMERG = 2300;<br>CTALM = 0; CTEM = 0; CTEP = 0; CTF = 0;"]
    Init --> Avance["T = T + Δt<br>DIA_MES = DIA_MES + 1<br>DIA_SEM = DIA_SEM + 1"]
    Avance --> CheckMes{"DIA_MES > 30"}
    CheckMes -- SI --> ResetMes["DIA_MES = 1<br>COMPRA_MES = 0"]
    ResetMes --> CheckSem{"DIA_SEM > 7"}
    CheckMes -- NO --> CheckSem
    CheckSem -- SI --> ResetSem["DIA_SEM = 1"]
    ResetSem --> CheckFLL{"T = FLL"}
    CheckSem -- NO --> CheckFLL
    CheckFLL -- SI --> Recibe["ST = ST + TP<br>IP = 0<br>FLL = ∞"]
    Recibe --> CheckDia{"Día de la<br>Semana"}
    CheckFLL -- NO --> CheckDia
    CheckDia -- 1, 3, 5 --> VDLMV["CD = 74 + 18r"]
    CheckDia -- 2, 4, 6 --> VDMJS["CD = 62 + 14r"]
    CheckDia -- 7 --> VDDOM["CD = 0"]
    VDLMV --> Consume["ST = ST - CD"]
    VDMJS --> Consume
    VDDOM --> Consume
    Consume --> CheckEmerg{"ST ≤ 2500"}
    CheckEmerg -- SI --> CompraEmerg["costo_emerg = C_UNIT_EMERG * PE<br>CTEM = CTEM + costo_emerg<br>ST = ST + PE"]
    CompraEmerg --> CostoAlm["CTALM = CTALM + (ST * CALM)"]
    CheckEmerg -- NO --> CostoAlm
    CostoAlm --> CheckReorden{"15 ≤ DIA_MES ≤ 20<br>y COMPRA_MES = 0"}
    CheckReorden -- SI --> GeneraDE["Genera DE<br>DE = ceil(10 - 2.58 ln(r))<br>IP = 1<br>COMPRA_MES = 1<br>FLL = T + DE<br>costo_pedido = C_UNIT_PED * TP<br>CTEP = CTEP + costo_pedido"]
    GeneraDE --> CheckFin{"T ≤ TF"}
    CheckReorden -- NO --> CheckFin
    CheckFin -- SI --> Avance
    CheckFin -- NO --> CalcRes["CÁLCULO DE RESULTADOS<br>CTF = CTALM + CTEM + CTEP"]
    CalcRes --> Print[/"IMPRIMIR RESULTADOS<br>CTF"/]

     Init:::initBox
     Avance:::process
     CheckMes:::decision
     ResetMes:::process
     CheckSem:::decision
     ResetSem:::process
     CheckFLL:::decision
     Recibe:::process
     CheckDia:::decision
     VDLMV:::process
     VDMJS:::process
     VDDOM:::process
     Consume:::process
     CheckEmerg:::decision
     CompraEmerg:::process
     CostoAlm:::process
     CheckReorden:::decision
     GeneraDE:::process
     CheckFin:::decision
     CalcRes:::process
     Print:::io
    classDef initBox fill:#fff,stroke:#000,stroke-width:1px,rx:10px,ry:10px,color:#000
    classDef process fill:#fff,stroke:#000,stroke-width:1px,color:#000
    classDef decision fill:#fff,stroke:#000,stroke-width:1px,color:#000
    classDef io fill:#fff,stroke:#000,stroke-width:1px,color:#000
