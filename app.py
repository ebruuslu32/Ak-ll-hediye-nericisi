import streamlit as st
import google.generativeai as genai
import os
import requests
from bs4 import BeautifulSoup
import re

GEMINI_ANAHTARI = "AIzaSyC5_ActnFp7AW2P2r05nZVwHEP7wa8JN5A"

# Configure Gemini API
genai.configure(api_key=GEMINI_ANAHTARI)
model = genai.GenerativeModel('gemini-1.5-flash')

def get_gift_suggestions(recipient_profile, interests, occasion, budget):
    prompt = f"""
    Bir hediye uzmanı gibi davran ve aşağıdaki bilgilere göre Türkçe hediye önerileri sun:
    Hediye Alınacak Kişinin Profili: {recipient_profile}
    Kişinin İlgi Alanları: {interests}
    Hediye Alma Nedeni: {occasion}
    Bütçe: {budget} TL

    Lütfen şunları sağla:
    1. Önerilen hediye fikirleri (en az 3 farklı ürün)
    2. Hediye önerisinin gerekçesi (kişinin profiline ve ilgi alanlarına uygunluğu)
    3. Hediye için yaklaşık fiyat aralıkları
    """
    response = model.generate_content(prompt)
    return response.text

def search_products(product_names):
    product_links = {}
    for product in product_names.split(","):
        product = product.strip()
        search_query = product + " satın al"
        search_url = f"https://www.google.com/search?q={search_query}&tbm=shop"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        try:
            response = requests.get(search_url, headers=headers, timeout=10)  # Timeout eklendi

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                links = soup.find_all('a', class_='shntl')
                if links:
                    for link in links:
                        href = link.get('href')
                        if href and href.startswith("https://"):  # Sadece tam linkler
                           product_links[product] = href
                           break # ilk bulduğu geçerli linki al
            else:
               st.warning(f"Hata oluştu, HTTP Status Code: {response.status_code} - {search_query}")
        except requests.exceptions.RequestException as e:
            st.warning(f"İstek hatası oluştu: {e} - {search_query}")

    return product_links

st.set_page_config(page_title="Akıllı Hediye Önerici", page_icon="🎁", layout="wide")

st.title("🎁 Akıllı Hediye Önerici")
st.write("Sevdikleriniz için mükemmel hediyeyi bulmanıza yardımcı olalım!")

st.markdown("### Hediye Önerisi Oluşturma")

col1, col2 = st.columns(2)

with col1:
    alici_profili = st.text_area("Hediye Alınacak Kişinin Profili (Yaşı, cinsiyeti, mesleği vb.)", height=100)
    ilgi_alanlari = st.text_input("Hediye Alınacak Kişinin İlgi Alanları (Hobiler, sevdiği şeyler, vs.)")
    hediye_nedeni = st.selectbox("Hediye Alma Nedeni Nedir?", ["Doğum Günü", "Yıl Dönümü", "Mezuniyet", "Yeni İş", "Sadece Sevindirmek İçin"])
with col2:
    butce = st.number_input("Bütçeniz Nedir? (TL)", min_value=50, max_value=10000, value=500)
    st.image("https://example.com/gift_image.jpg", caption="Mükemmel Hediye", use_column_width=True)

if st.button("Hediye Önerisi Al") and alici_profili and ilgi_alanlari and hediye_nedeni and butce:
    with st.spinner("Hediye önerileri oluşturuluyor..."):
        hediye_onerileri = get_gift_suggestions(alici_profili, ilgi_alanlari, hediye_nedeni, butce)
        st.markdown(hediye_onerileri)

        # Ürünleri bul ve bağlantılarını getir
        product_names_list = [line.split(". ")[1].strip() for line in hediye_onerileri.split("\n") if line.strip().startswith("1.") or line.strip().startswith("2.") or line.strip().startswith("3.") or line.strip().startswith("4.") or line.strip().startswith("5.")]
        product_names = ",".join(product_names_list)
        if product_names:
            product_links = search_products(product_names)
            st.markdown("### Ürün Satın Alma Bağlantıları")
            if product_links:
                for product, link in product_links.items():
                    st.markdown(f"- [{product}]({link})")
            else:
                st.warning("Ürünler için satın alma linkleri bulunamadı.")



st.sidebar.markdown("""
## Hakkında
Bu Akıllı Hediye Önerici, Google'ın Gemini AI'sını kullanarak kişiselleştirilmiş hediye önerileri sunar.
Hediye alacağınız kişinin profilini, ilgi alanlarını, hediye alma nedeninizi ve bütçenizi belirterek başlayın!
""")