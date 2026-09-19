from openai import OpenAI
import os


class MelOpenAIAssistant:
    """OpenAI API altyapısını kullanan The Mel Project asistan sınıfı."""

    def __init__(self, api_key=, model="gpt-4o-mini"):
        # API anahtarını doğrudan verebilir ya da OPENAI_API_KEY çevre değişkeninden almasını sağlayabilirsiniz
        self.client = OpenAI(api_key=api_key)
        self.model = model
        
        # Asistanın kimliğini belirleyen sistem talimatı (System Prompt)
        self.messages = [
            {
                "role": "system",
                "content": (
                    "Sen The Mel Project adlı akıllı yerel asistan modülüsün. "
                    "ANOE işletim sistemi çekirdeği ile uyumlu çalışıyorsun. "
                    "Geliştiriciye Python yazılımı, sistem optimizasyonu ve genel konularda yardımcı oluyorsun."
                )
            }
        ]

    def chat(self, user_input):
        self.messages.append({"role": "user", "content": user_input})
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                temperature=0.7
            )
            reply = response.choices[0].message.content
            self.messages.append({"role": "assistant", "content": reply})
            return reply
        except Exception as e:
            return f"[API Bağlantı Hatası] OpenAI sunucusuyla iletişim kurulamadı: {e}"


if __name__ == "__main__":
    print("========================================================")
    print("         THE MEL PROJECT - OPENAI DESTEKLİ MOD          ")
    print("========================================================")
    print("Çıkış yapmak için 'q', 'exit' veya 'çıkış' yazabilirsiniz.\n")

    # İsteğe bağlı olarak api_key="sk-..." parametresi ekleyebilirsiniz. 
    # Varsayılan olarak sistemdeki OPENAI_API_KEY ortam değişkenini kontrol eder.
    mel = MelOpenAIAssistant(model="gpt-4o-mini")

    while True:
        try:
            user_input = input("Geliştirici > ").strip()
            if not user_input:
                continue
            if user_input.lower() in ["q", "exit", "çıkış"]:
                print("\nThe Mel Project güvenle kapatılıyor. İyi günler!")
                break

            reply = mel.chat(user_input)
            print(f"\nMel > {reply}\n" + "-" * 55)

        except (KeyboardInterrupt, EOFError):
            print("\nOturum sonlandırıldı.")
            break