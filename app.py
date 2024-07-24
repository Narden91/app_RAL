from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

def calcola_netto_mensile(citta, ral, mensilita, addizionale_regionale=None, addizionale_comunale=None):
    # Costanti
    ALIQUOTA_INPS = 0.0919

    # Funzione per calcolare l'IRPEF
    def calcola_irpef(imponibile):
        if imponibile <= 15000:
            return imponibile * 0.23
        elif imponibile <= 28000:
            return 3450 + (imponibile - 15000) * 0.25
        elif imponibile <= 50000:
            return 6700 + (imponibile - 28000) * 0.35
        else:
            return 14400 + (imponibile - 50000) * 0.43

    # Funzione per calcolare la detrazione
    def calcola_detrazione(imponibile):
        if imponibile <= 15000:
            return 1880
        elif imponibile <= 28000:
            return 1910 + (28000 - imponibile) * 1.190 / 13000
        elif imponibile <= 50000:
            return 1910 * (50000 - imponibile) / 22000
        else:
            return 0

    # Calcolo della base imponibile IRPEF
    contributi_inps = ral * ALIQUOTA_INPS
    base_imponibile = ral - contributi_inps

    # Calcolo dell'IRPEF e della detrazione
    irpef_lorda = calcola_irpef(base_imponibile)
    detrazione = calcola_detrazione(base_imponibile)
    irpef_netta = max(irpef_lorda - detrazione, 0)

    # Calcolo delle addizionali
    if citta.lower() == "roma":
        addizionale_regionale = base_imponibile * 0.0173
        addizionale_comunale = base_imponibile * 0.009
    elif citta.lower() == "milano":
        addizionale_regionale = base_imponibile * 0.0123
        addizionale_comunale = base_imponibile * 0.008
    else:
        addizionale_regionale = base_imponibile * addizionale_regionale
        addizionale_comunale = base_imponibile * addizionale_comunale

    # Calcolo del netto annuale
    netto_annuale = ral - contributi_inps - irpef_netta - addizionale_regionale - addizionale_comunale

    # Calcolo del netto mensile
    netto_mensile = netto_annuale / mensilita

    return netto_mensile

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/calcola', methods=['POST'])
def calcola():
    data = request.json
    citta = data['citta']
    ral = float(data['ral'])
    mensilita = int(data['mensilita'])
    addizionale_regionale = float(data['addizionale_regionale']) / 100 if data['addizionale_regionale'] else None
    addizionale_comunale = float(data['addizionale_comunale']) / 100 if data['addizionale_comunale'] else None

    netto_mensile = calcola_netto_mensile(citta, ral, mensilita, addizionale_regionale, addizionale_comunale)
    
    return jsonify({'netto_mensile': round(netto_mensile, 2)})

if __name__ == '__main__':
    app.run(debug=True)