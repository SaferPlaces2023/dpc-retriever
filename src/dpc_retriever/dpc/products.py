from .DPCProduct import DPCProduct, DPCException       



# DOC: List of available products    



_AVALIABLE_PRODUCTS = []        
        
        
VMI = DPCProduct(
    code = "VMI",
    name = "Vertical Maximum Intensity",
    description="E’ un prodotto che rappresenta il valore massimo di riflettività [dBz] presente sulla verticale di ogni punto. Il VMI viene utilizzato per un monitoraggio generale, in quanto permette di distinguere le zone in cui sono in corso fenomeni di un certo rilievo e di classificarli in base alla loro tipologia (fronti, sistemi convettivi).",
    update_frequency="5T"
)
_AVALIABLE_PRODUCTS.append(VMI)

SRI = DPCProduct(
    code = "SRI",
    name = "Surface Rainfall Intensity",
    description="E’ un prodotto elaborato attraverso specifiche catene operative sviluppate presso il CFC, combinando i dati della rete radar con la rete pluviometrica, con l’obiettivo di fornire una stima dell’intensità di precipitazione al suolo (mm/h).",
    update_frequency="5T"
)
_AVALIABLE_PRODUCTS.append(SRI)

SRT1 = DPCProduct(
    code = "SRT1",
    name = "Cumulata di precipitazione in 1 ora",
    description="E’ un prodotto che rappresenta la cumulata di precipitazione (mm) nell’ultima ora sulla base dell’integrazione del dato radar SRI (sopra menzionato) su 1 ora e i dati della rete a terra",
    update_frequency="5T"
)
SRT3 = DPCProduct(
    code = "SRT3",
    name = "Cumulata di precipitazione in 3 ore",
    description="Le cumulataSRT3 è ottenuta esclusivamente a partire dai dati “raw” della rete a terra provenienti dalle stazioni pluviometriche (circa 3000), disponibili nell’ambito della rete dei centri funzionali, e successivamente oggetto di elaborazione attraverso tecniche di interpolazione da parte del Dipartimento al fine di ottenere la distribuzione omogenea dell’informazione sul territorio sui diversi intervalli temporali.",
    update_frequency="1H"
)
SRT6 = DPCProduct(
    code = "SRT6",
    name = "Cumulata di precipitazione in 6 ore",
    description="Le cumulataSRT6 è ottenuta esclusivamente a partire dai dati “raw” della rete a terra provenienti dalle stazioni pluviometriche (circa 3000), disponibili nell’ambito della rete dei centri funzionali, e successivamente oggetto di elaborazione attraverso tecniche di interpolazione da parte del Dipartimento al fine di ottenere la distribuzione omogenea dell’informazione sul territorio sui diversi intervalli temporali.",
    update_frequency="1H"
)
SRT12 = DPCProduct(
    code = "SRT12",
    name = "Cumulata di precipitazione in 12 ore",
    description="Le cumulataSRT12 è ottenuta esclusivamente a partire dai dati “raw” della rete a terra provenienti dalle stazioni pluviometriche (circa 3000), disponibili nell’ambito della rete dei centri funzionali, e successivamente oggetto di elaborazione attraverso tecniche di interpolazione da parte del Dipartimento al fine di ottenere la distribuzione omogenea dell’informazione sul territorio sui diversi intervalli temporali.",
    update_frequency="1H"
)
SRT24 = DPCProduct(
    code = "SRT24",
    name = "Cumulata di precipitazione in 24 ore",
    description="Le cumulataSRT24 è ottenuta esclusivamente a partire dai dati “raw” della rete a terra provenienti dalle stazioni pluviometriche (circa 3000), disponibili nell’ambito della rete dei centri funzionali, e successivamente oggetto di elaborazione attraverso tecniche di interpolazione da parte del Dipartimento al fine di ottenere la distribuzione omogenea dell’informazione sul territorio sui diversi intervalli temporali.",
    update_frequency="1H"
)
_AVALIABLE_PRODUCTS.extend([SRT1, SRT3, SRT6, SRT12, SRT24])

IR108 = DPCProduct(
    code = "IR108",
    name = "Copertura nuvolosa",
    description="Prodotto derivato da elaborazione del canale IR 10.8 di satelliti MSG (Meteosat Second Generation Images).",
    update_frequency="5T"
)
_AVALIABLE_PRODUCTS.append(IR108)

TEMP = DPCProduct(
    code = "TEMP",
    name = "Mappa delle Temperature",
    description="Prodotto che è ottenuto a partire dai dati “raw ”della rete a terra provenienti dalle stazioni termometriche (circa 2600), disponibili nell’ambito della rete dei centri funzionali, e successivamente oggetto di elaborazione attraverso tecniche di interpolazione da parte del Dipartimento al fine di ottenere la distribuzione omogenea dell’informazione sul territorio.",
    update_frequency="1H"
)
_AVALIABLE_PRODUCTS.append(TEMP)

LTG = DPCProduct(
    code = "LTG",
    name = "Mappa dei fulmini",
    description="Il prodotto, fornito dal Aeronautica Militare - CNMCA, rappresenta una stima in tempo reale della frequenza assoluta di fulminazioni proveniente dalla rete LAMPINET.",
    update_frequency="10T"
)
_AVALIABLE_PRODUCTS.append(LTG)

AMV = DPCProduct(
    code = "AMV",
    name = "Direzione e intensità del vento in Quota",
    description="Il prodotto rappresenta il campionamento dei valori puntuali contenuti nel prodotto MPEF (Meteorological Products Extraction Facility) denominato Atmospheric Motion Vector, su una griglia di 50x50 kmq",
    update_frequency="20T"
)
_AVALIABLE_PRODUCTS.append(AMV)

HRD = DPCProduct(
    code = "HRD",
    name = "Heavy Rain Detection",
    description = "E’ un prodotto «Non Standard» in quanto si basa su un approccio multisensore-multiparametrico, con l’obiettivo di individuare delle aree in cui sono in corso precipitazioni particolarmente intense, persistenti e/o di natura temporalesca a cui associare un Indice di Severità oltre che la possibile traiettoria nel brevissimo termine. Tale Indice è individuato sulla base di una specifica catena operativa, sviluppata presso il CFC, che combina una serie di grandezze meteo (intensità di precipitazione, contenuto d’acqua liquida equivalente, probabilità di grandine, top della nube, persistenza, cumulata di precipitazione) stimate in tempo reale attraversospecifici prodotti generati dai dati provenienti da diversi sensori (radar, satelliti, rete di fulminazioni e rete pluviometrica).",
    update_frequency = "5T"
)
_AVALIABLE_PRODUCTS.append(HRD)

RADAR = DPCProduct(
    code = "RADAR_STATUS",
    name = "Radar",
    description="Ubicazione dei siti. Verde: ON - Rosso: OFF",
    update_frequency = None
)
_AVALIABLE_PRODUCTS.append(RADAR)

CAPPI1 = DPCProduct(
    code = "CAPPI1",
    name = "E’ un prodotto che rappresenta il valore di riflettività [dBz] presente sulla sezione orizzontale del volume polare scansionato ad una quota fissata di 1000 m slm.",
    description = "Constant Altitude Plan Position Indicator",
    update_frequency = "10T"
)
CAPPI2 = DPCProduct(
    code = "CAPPI2",
    name = "E’ un prodotto che rappresenta il valore di riflettività [dBz] presente sulla sezione orizzontale del volume polare scansionato ad una quota fissata di 2000 m slm.",
    description = "Constant Altitude Plan Position Indicator",
    update_frequency = "10T"
)
CAPPI3 = DPCProduct(
    code = "CAPPI3",
    name = "E’ un prodotto che rappresenta il valore di riflettività [dBz] presente sulla sezione orizzontale del volume polare scansionato ad una quota fissata di 3000 m slm.",
    description = "Constant Altitude Plan Position Indicator",
    update_frequency = "10T"
)
CAPPI4 = DPCProduct(
    code = "CAPPI4",
    name = "E’ un prodotto che rappresenta il valore di riflettività [dBz] presente sulla sezione orizzontale del volume polare scansionato ad una quota fissata di 4000 m slm.",
    description = "Constant Altitude Plan Position Indicator",
    update_frequency = "10T"
)
CAPPI5 = DPCProduct(
    code = "CAPPI5",
    name = "E’ un prodotto che rappresenta il valore di riflettività [dBz] presente sulla sezione orizzontale del volume polare scansionato ad una quota fissata di 5000 m slm.",
    description = "Constant Altitude Plan Position Indicator",
    update_frequency = "10T"
)
CAPPI6 = DPCProduct(
    code = "CAPPI6",
    name = "E’ un prodotto che rappresenta il valore di riflettività [dBz] presente sulla sezione orizzontale del volume polare scansionato ad una quota fissata di 6000 m slm.",
    description = "Constant Altitude Plan Position Indicator",
    update_frequency = "10T"
)
CAPPI7 = DPCProduct(
    code = "CAPPI7",
    name = "E’ un prodotto che rappresenta il valore di riflettività [dBz] presente sulla sezione orizzontale del volume polare scansionato ad una quota fissata di 7000 m slm.",
    description = "Constant Altitude Plan Position Indicator",
    update_frequency = "10T"
)
CAPPI8 = DPCProduct(
    code = "CAPPI8",
    name = "E’ un prodotto che rappresenta il valore di riflettività [dBz] presente sulla sezione orizzontale del volume polare scansionato ad una quota fissata di 8000 m slm.",
    description = "Constant Altitude Plan Position Indicator",
    update_frequency = "10T"
)
_AVALIABLE_PRODUCTS.extend([CAPPI1, CAPPI2, CAPPI3, CAPPI4, CAPPI5, CAPPI6, CAPPI7, CAPPI8])


def product_by_code(code):
    """
    Returns the product with the specified code.
    """
    for product in _AVALIABLE_PRODUCTS:
        if product.code == code:
            return product
    return None