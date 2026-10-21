import json
path = '/sessions/inspiring-confident-ritchie/mnt/outputs/work/studios_final.json'
studios = json.load(open(path, encoding='utf-8'))
def c(j, d, f, t): return {"jour": j, "debut": d, "fin": f, "type": t}
new = {
  "nom": "Pandi Panda Yoga", "arr": "Villeurbanne", "quartier": "Cusset",
  "site": "https://pandipandayoga.com/",
  "adresse": "268 rue du 4 août 1789, 69100 Villeurbanne",
  "cours": [
    c("Lundi","18h15","19h15","Vinyasa Yoga"),
    c("Lundi","19h00","20h00","Vinyasa Yoga (intermédiaire)"),
    c("Lundi","19h30","20h30","Vinyasa Yoga"),
    c("Mardi","12h30","13h20","Vinyasa Yoga"),
    c("Mardi","18h00","19h00","Yin Yoga"),
    c("Mardi","19h00","20h00","Yoga Aérien"),
    c("Mardi","20h00","21h00","Hatha Yoga"),
    c("Mercredi","12h30","13h30","Yoga Aérien"),
    c("Mercredi","18h05","19h05","Yoga Aérien"),
    c("Mercredi","19h15","20h15","Vinyasa Yoga (intermédiaire)"),
    c("Jeudi","10h30","11h30","Yoga Postnatal Maman Bébé"),
    c("Jeudi","12h30","13h30","Yoga Aérien Prénatal"),
    c("Jeudi","18h00","19h00","Hatha Yoga"),
    c("Jeudi","19h05","20h05","Yoga Aérien Acro"),
    c("Vendredi","12h30","13h30","Yoga Aérien"),
    c("Samedi","10h00","11h00","Yoga Aérien"),
    c("Samedi","11h15","12h15","Vinyasa Yoga"),
    c("Dimanche","10h00","11h00","Yoga Aérien (initiation)"),
    c("Dimanche","11h15","12h15","Yoga Aérien (débutant)"),
  ]}
assert not any(s['nom']==new['nom'] for s in studios)
studios.append(new)
json.dump(studios, open(path,'w',encoding='utf-8'), ensure_ascii=False, indent=2)
print(len(studios), sum(len(s['cours']) for s in studios))
