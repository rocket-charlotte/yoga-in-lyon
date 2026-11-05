import json
path = '/sessions/inspiring-confident-ritchie/mnt/outputs/work/studios_final.json'
studios = json.load(open(path, encoding='utf-8'))
def c(j, d, f, t): return {"jour": j, "debut": d, "fin": f, "type": t}
# Planning relevé sur le widget bsport de https://fauves-yoga.com/planning/ (semaine du 9 nov. 2026).
# Cours de yoga et de Pilates au sol uniquement : Reformer, Kids club, cercle de parole et danse avec bébé non repris.
new = {
  "nom": "Fauves Yoga", "arr": "Lyon 5e", "quartier": "Vieux Lyon",
  "site": "https://fauves-yoga.com/",
  "adresse": "23 rue Tramassac, 69005 Lyon",
  "cours": [
    c("Mardi","09h45","10h35","Yoga sur chaise"),
    c("Mardi","12h00","13h30","Vinyasa Patio"),
    c("Mardi","12h15","13h00","Yoga Sculpt express 45' (Pilates & renfo)"),
    c("Mardi","13h00","13h45","Yoga Vinyasa express 45'"),
    c("Mardi","14h00","14h50","Yoga Prénatal"),
    c("Mardi","15h00","15h50","Yoga Postnatal avec bébé"),
    c("Mardi","17h00","17h50","Yin Yoga & Bain sonore"),
    c("Mardi","18h15","19h10","Yoga Vinyasa"),
    c("Mardi","19h15","20h10","Power Yoga"),
    c("Mardi","20h15","21h10","Yoga Yin Yang"),
    c("Mercredi","08h00","08h50","Yoga Prénatal"),
    c("Mercredi","09h00","09h50","Yoga Postnatal avec bébé"),
    c("Mercredi","10h00","10h55","Yoga parent-enfant (3-8 ans)"),
    c("Mercredi","11h00","11h55","Yoga enfants (5-10 ans)"),
    c("Mercredi","12h00","12h55","Power Yoga"),
    c("Mercredi","13h00","13h55","Yoga Vinyasa débutants"),
    c("Mercredi","14h00","14h50","Pilates"),
    c("Mercredi","15h00","15h55","Pilates"),
    c("Mercredi","18h15","19h05","Hot Slow Flow"),
    c("Mercredi","19h15","20h10","Yoga Sculpt (Pilates & renfo)"),
    c("Mercredi","20h15","21h10","Souplesse"),
    c("Jeudi","07h30","08h25","Yoga de l'Énergie"),
    c("Jeudi","08h30","09h25","Yoga de l'Énergie"),
    c("Jeudi","09h30","10h45","Hatha Yoga"),
    c("Jeudi","10h45","12h00","Yoga Danse"),
    c("Jeudi","12h15","13h05","Hot Vinyasa"),
    c("Jeudi","13h15","14h05","Slow Flow"),
    c("Jeudi","15h05","15h55","Yoga Sculpt (Pilates & renfo)"),
    c("Jeudi","17h00","17h55","Yoga enfants (5-10 ans)"),
    c("Jeudi","18h15","19h05","Yoga Vinyasa"),
    c("Jeudi","19h15","20h10","Yoga Danse"),
    c("Jeudi","20h15","21h10","Hot Vinyasa"),
    c("Dimanche","08h30","09h25","Yoga Vinyasa"),
    c("Dimanche","09h30","10h20","Power Yoga"),
    c("Dimanche","10h30","12h00","Yoga Brunch"),
    c("Dimanche","17h00","17h50","Yoga Vinyasa"),
    c("Dimanche","18h00","18h50","Yin Yoga"),
  ]}
assert not any(s['nom']==new['nom'] for s in studios)
studios.append(new)
json.dump(studios, open(path,'w',encoding='utf-8'), ensure_ascii=False, indent=2)
print(len(studios), sum(len(s['cours']) for s in studios))
