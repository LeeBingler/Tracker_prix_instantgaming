from tkinter import Tk,Frame,Label,YES,Entry,Button,Checkbutton,BooleanVar
from PIL import ImageTk, Image
window = ""
def interface():
    #creation fenetre
    global window
    window = Tk()
    window.title("Tracker")
    window.geometry("500x500")
    window.config(background="#EEE8AA")
    
    #creation frame principale
    frame = Frame(window, bg="#EEE8AA")
    
    #creation sous boite 
    lower_frame = Frame(frame,bg="#EEE8AA")
    mid_frame = Frame(frame,bg="#EEE8AA")
    oui_frame = Frame(frame,bg="#EEE8AA")
    
    #creation image
    img = Image.open('logo.png')
    img = ImageTk.PhotoImage(img)
    panel = Label(frame, image = img)
    panel.pack(side = "top", fill = "both", expand = "yes")
    
    #creation texte
    label_wanted_price = Label(mid_frame, text='prix voulu (mettre un . pas une virgule)', bg="#EEE8AA" , fg="black").pack()
    label_URL = Label(lower_frame, text='URL', bg="#EEE8AA" , fg="black").pack()
    label_email = Label(frame, text='Adresse email', bg="#EEE8AA" , fg="black").pack()

    #creation insertion texte
    insertion_wanted_price = Entry(mid_frame, bg="#EEE8AA" , fg="black")
    insertion_URL = Entry(lower_frame, bg="#EEE8AA" , fg="black")
    insertion_email = Entry(frame, bg="#EEE8AA" , fg="black")
    insertion_wanted_price.pack()
    insertion_URL.pack()
    insertion_email.pack()
    
    #creation bouton
    validity_button = Button(lower_frame, text="valider", bg="white", command=lambda :choose(insertion_email.get(),insertion_URL.get(),insertion_wanted_price.get(),cd.get())) #modif command pour changer la fonction du bouton + lambda obliger sinon code ce lance tout seul
    validity_button.pack()
    
    #creation checkbox
    def isChecked():
        if cd.get() == 1:
            return True
        elif cd.get() == 0:
            return False

    cd = BooleanVar()
    Checkbutton(lower_frame, text="Instant gaming", variable=cd, onvalue=True, offvalue=False, command=isChecked()).pack()
    
    #affiche la fenetre
    oui_frame.pack(expand=YES)
    mid_frame.pack(expand=YES)
    lower_frame.pack(expand=YES)
    frame.pack(expand=YES)
    window.mainloop()
    window.quit()


def alert(title, message, kind='error', hidemain=True):
    #affiche message d'alerte
    from tkinter import messagebox
    if kind not in ('error', 'warning', 'info'):
        raise ValueError('Unsupported alert kind.')

    show_method = getattr(messagebox, 'show{}'.format(kind))
    show_method(title, message)

def recup_jeu_instantgaming(product_url):
    # Recherche sur la page donnée par l'utilisateur du prix et du titre actuelle du jeu
    from bs4 import BeautifulSoup
    import requests
    headers = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:92.0) Gecko/20100101 Firefox/92.0"
    }
    
    #variable de stockage du nom + prix des jeux
    nbre_de_jeu = len(product_url)
    product_names = [""]*nbre_de_jeu
    product_price = [""]*nbre_de_jeu
    instance = ""
    for i in range(nbre_de_jeu) :
        page = requests.get(product_url[i],headers=headers)
        soup = BeautifulSoup(page.content, 'html.parser')
        product_names[i] = soup.find("h1",class_ = "game-title").text
        product_price[i] = soup.find("div",class_= "panel item wide").find("div", class_="total").text
        
        # on garde uniquement le nombre
        for x in range(5):
            instance += product_price[i][x]
        product_price[i] = instance
    
    return product_names, product_price

def send_mail(email_receiver,mail_content):
    #envoie un mail depuis une boite mail créé pour l'occasion
    import smtplib
    from email.mime.text import MIMEText
    
    SMTP_SERVER = "smtp.mail.yahoo.com"
    SMTP_PORT = 465
    SMTP_USERNAME = "trackerprix@yahoo.com"
    SMTP_PASSWORD = "lwszomgzprjubeyy"
    EMAIL_FROM = "trackerprix@yahoo.com"
    EMAIL_TO = email_receiver
    EMAIL_SUBJECT = "Tracker de prix"

    msg = MIMEText(mail_content)
    msg['Subject'] = EMAIL_SUBJECT
    msg['From'] = EMAIL_FROM 
    msg['To'] = EMAIL_TO
    mail = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT,timeout=20)
    mail.login(SMTP_USERNAME, SMTP_PASSWORD)
    mail.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())
    mail.quit()

def new_acc(email,url,wp) :
    #créé un nouveau compte dans le csv
    import csv
    with open('account.csv','r',newline='', encoding='utf-8') as fichiercsv :
        reader = csv.DictReader(fichiercsv)
        for row in reader:
            
            if row['email'] == email and row['url'] == url :
                alert("Existe déjà !","Ce jeu est déjà surveillé par ce mail")
                return False

    with open('account.csv','a',newline='', encoding='utf-8') as fichiercsv :
        writer=csv.writer(fichiercsv)
        writer.writerow([email,url,wp])
        return True

def compare(products_price , wanted_price):
    #compare les prix des produits actuelles avec les prix voulu par l'utilisateur 
    
    for i in range(len(products_price)):
        if products_price[i] < wanted_price[i]:
            return 1
            
        elif products_price[i] == wanted_price[i]:
            return 2
        
        elif products_price[i] > wanted_price[i]:
            return 3

def main_instantgaming(email,games_url, wanted_price):
    import time
    #verif si l'email, le prix et url sont valide
    if not("@" in email and (email.endswith(".com") or email.endswith(".fr")))  :
        alert("Mail","Email invalide")
    elif not "." in wanted_price :
        alert("Prix voulu","Le prix doit être ecrit sous la forme 23.20")
    elif  not (games_url.startswith("http://") or  games_url.startswith("https://")) :
        alert("Url","Url invalide")
    elif not new_acc(email,games_url,wanted_price):
        pass
    else :
        alert("Tout est bon","L'article est traqué (ne pas fermer la fenêtre tant que l'on veut que l'article soit traqué)",kind = 'info')
        while True :
            games_names , games_prices = recup_jeu_instantgaming(games_url)
            print(games_names,games_prices)
            prix_comparer = compare(games_prices, wanted_price)
            if prix_comparer == 1:
                send_mail(email,"Le prix est plus bas que ce que vous avez demandé.")
            if prix_comparer == 2:
                send_mail(email,"Le prix est au prix que vous avez demandé.")
            if prix_comparer == 3 :
                send_mail(email,"le prix est plus haut que ce que vous avez demadé.")
            
            #attends 24h avant de ce relancer
            time.sleep(86400)

            
            
def choose(email,games_url,wp,check):
    #verifie si la checkbox est coché ou non
    if check:
        main_instantgaming(email,games_url,wp)
    elif not check:
        print("j'ai essayé de l'universalisé mais ça ne marche pas")
    else:
        print("Cassé")

interface()
