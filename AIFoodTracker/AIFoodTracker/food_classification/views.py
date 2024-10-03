from django.shortcuts import render
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np
from django.http import HttpResponse
import os
import requests
from bs4 import BeautifulSoup

def index(request):
    return render(request,'index.html')

def contact(request):
    return render(request,'contact.html')

# Vücut Kitle İndeksi Hesaplama Sayfası
def bmi_calculator(request):
    bmi_result = None
    status = None
    recommendation = None

    if request.method == 'POST':
        weight = float(request.POST.get('weight'))
        height = float(request.POST.get('height')) / 100  # cm to meters
        age = int(request.POST.get('age'))
        gender = request.POST.get('gender')  # 'male' or 'female'

        bmi_result = round(weight / (height ** 2), 2)

        # BMI evaluation and recommendations
        if bmi_result < 18.5:
            status = "Underweight"
            recommendation = (
                "It is recommended that you gain weight. You should focus on a balanced diet "
                "and exercises that strengthen your muscle mass. Consulting a nutritionist "
                "who specializes in your age and gender may be beneficial."
            )
        elif 18.5 <= bmi_result < 25:
            status = "Normal weight"
            recommendation = (
                "Your weight is ideal. Continue to maintain a healthy lifestyle with a balanced "
                "diet and regular exercise. Be mindful of maintaining your muscle mass according "
                "to your age and gender."
            )
        elif 25 <= bmi_result < 30:
            status = "Overweight"
            recommendation = (
                "You have a little extra weight. You can aim for weight loss through a balanced "
                "diet and regular exercise. It is recommended to do cardio exercises, especially "
                "to reduce fat in the abdominal area. Depending on gender, fat accumulation in "
                "this area may increase the risk of heart disease, particularly in men."
            )
        elif 30 <= bmi_result < 35:
            status = "Class 1 Obesity"
            recommendation = (
                "You are at risk of obesity. It is advised to take steps to lose weight in collaboration "
                "with a nutritionist and doctor. The risk of chronic diseases can increase based on "
                "your age and gender, so it is important to undergo a health check."
            )
        elif 35 <= bmi_result < 40:
            status = "Class 2 Obesity"
            recommendation = (
                "Your obesity level has increased. You may need to lose weight urgently to reduce the risk "
                "of health issues. It is crucial to create a balanced diet and regular exercise plan. "
                "Hormonal levels and metabolic changes can vary by gender, so professional advice should be sought."
            )
        else:  # BMI >= 40
            status = "Class 3 Obesity"
            recommendation = (
                "You have a weight level that poses serious health risks. You should seek immediate medical help "
                "and attempt to lose weight under the guidance of a nutritionist and doctor. The risk of complications "
                "may increase with age and gender, so professional support is essential."
            )

    return render(request, 'bmi_calculator.html', {
        'bmi_result': bmi_result,
        'status': status,
        'recommendation': recommendation
    })


# Model Yükleme ve Yemek Sınıflandırma Sayfası
def food_classification(request):
    uploaded_image_url = None  # Yüklenen resmin URL'si için değişken
    result = None  # Initialize result variable
    calori=None

    if request.method == 'POST':
        # 'food_image' anahtarının mevcut olup olmadığını kontrol edin
        if request.FILES['image']:
            model = load_model('best_mobilenetv2_model.h5', compile=False)
            class_names = [
                'Ispanak Yemeği', 'Hamsi Tava', 'Tarhana Çorbası', 'Döner',
                'Kalburabastı', 'Turşu', 'Çilek', 'Tulumba Tatlısı',
                'Dondurma', 'Lahmacun', 'Portakal', 'Çoban Salatası',
                'Üzüm', 'Taş Kebabı', 'Mantı', 'Pilav', 'Şeftali', 'Kokoreç',
                'Biber Dolma', 'Baklava', 'Pırasa', 'Çay', 'Yayla Çorbası',
                'Sulu Bamya Yemeği', 'Ayran', 'Ekmek', 'Havuç', 'Patates Salatası',
                'Sulu Patates Yemeği', 'Mercimek Çorbası', 'Erik', 'Adana Kebap',
                'Domates Çorbası', 'Menemen', 'Zeytinyağlı Fasulye',
                'Sulu Mercimek Yemeği', 'Elma', 'Çiğ Köfte', 'Tantuni',
                'Kavun', 'Siyah Zeytin', 'Et Sote', 'Mercimek Köftesi', 'Kısır',
                'Sulu Kuru Fasulye Yemeği', 'Sütlaç', 'Salatalık', 'Yoğurt',
                'Mumbar Dolması', 'Cacık', 'Kemal Paşa Tatlısı', 'Şehriye Çorbası',
                'İskender', 'Patates Kızartması', 'Su Böreği', 'Karnıyarık',
                'Çanak Enginar', 'Sulu Nohut Yemeği', 'Omlet', 'Levrek',
                'Sucuklu Yumurta', 'Kazandibi', 'Midye Dolma', 'Kıymalı Pide',
                'Lokma', 'İçli Köfte', 'Tavuk Sote', 'Brokoli', 'Anne Köftesi',
                'Bulgur Pilavı', 'Sulu Barbunya Yemeği', 'Yeşil Zeytin',
                'Kayısı', 'Sandviç', 'Sulu Bezelye Yemeği', 'Mango',
                'Çipura', 'Patates Püresi', 'Kiraz', 'Domates', 'Yaprak Sarma'
            ]

            # Resmi hazırlama ve modele uygun hale getirme
            img = request.FILES['image']  # Burada 'food_image' adını kullandık
            img_path = f'./temp/{img.name}'  # Resmi geçici bir dosyaya kaydet

            # Geçici dosyayı oluştur
            with open(img_path, 'wb+') as destination:
                for chunk in img.chunks():
                    destination.write(chunk)

            # Resmi sınıflandırma için hazırlayın
            img_array = prepare_image(img_path)
            predictions = model.predict(img_array)
            predicted_class_index = np.argmax(predictions, axis=1)
            predicted_class_name = class_names[predicted_class_index[0]]

            result = requests.get("https://www.diyetkolik.com/kac-kalori/arama/{}".format(predicted_class_name))
            html = result.content
            soup = BeautifulSoup(html, "html.parser")
            food_list = soup.find("div", attrs={'class': 'p15 kurumsalBorder backgroundWhite'})
            food = food_list.find_all("span", attrs={'class': 'd-block'})
            x = food[0]
            calori = x.text
            calori = int(calori.split('•')[1].split()[0])

            result = "{}, 1 portion".format(predicted_class_name)

            # Yüklenen resmin URL'sini ayarlayın
            uploaded_image_url = img_path

            os.remove(img_path)

        else:
            return HttpResponse("Lütfen bir resim yükleyin.")

    return render(request, 'food_classification.html', {
        'result': result,
        'uploaded_image_url': uploaded_image_url,
        'calorie_amount': calori  # Kalori değişkeni burada
    })



# Resmi modele uygun hale getiren fonksiyon
def prepare_image(img_path, target_size=(224, 224)):
    img = image.load_img(img_path, target_size=target_size)
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array /= 255.
    return img_array
