"""
Calcoli puri (senza dipendenze da QGIS) per ancorare la sezione a un DTM.

La sezione 2D ha una propria quota locale "v". Per portarla alla quota reale
si legge la Z del DTM nei punti A e B e si confronta con la quota locale del
profilo superiore della sezione (il "tetto", cioè la superficie topografica)
ai due estremi.
"""


def edge_top(vertices, u_edge, width, rel_tol=0.01):
    """Quota locale più alta tra i vertici vicini all'estremo ``u_edge``.

    ``vertices`` è una lista di coppie (u, v), con u = distanza orizzontale
    lungo la sezione e v = quota locale. Vengono considerati i vertici entro
    ``rel_tol * width`` dall'estremo (di default l'1% della larghezza), per
    tollerare i bordi leggermente inclinati dei poligoni digitalizzati.
    Restituisce None se non ci sono vertici in quella fascia.
    """
    tol = abs(width) * rel_tol
    valori = [v for u, v in vertices if abs(u - u_edge) <= tol]
    return max(valori) if valori else None


def dtm_anchor(z_a, z_b, ref_a, ref_b, esagerazione, cos_a, fit_b):
    """Calcola lo spostamento verticale per far coincidere la sezione col DTM.

    z_a, z_b      quota del DTM nei punti A e B
    ref_a, ref_b  quota locale del tetto della sezione in A e in B
                  (prima dell'esagerazione verticale)
    esagerazione  fattore di esagerazione verticale
    cos_a         coseno dell'angolo di rotazione (1 = sezione verticale)
    fit_b         se True, la differenza residua in B viene distribuita
                  linearmente lungo la sezione (deformazione verticale)

    Restituisce (z_base, shear, mismatch):
      z_base    da sommare alla quota di ogni punto
      shear     differenza da distribuire linearmente da A (0) a B (1)
      mismatch  differenza residua in B quando si ancora solo in A
    """
    z_base = z_a - ref_a * esagerazione * cos_a
    tetto_b = z_base + ref_b * esagerazione * cos_a
    mismatch = z_b - tetto_b
    shear = mismatch if fit_b else 0.0
    return z_base, shear, mismatch
