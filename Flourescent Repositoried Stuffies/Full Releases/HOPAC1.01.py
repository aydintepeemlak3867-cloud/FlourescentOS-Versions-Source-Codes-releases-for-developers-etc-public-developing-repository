import json
from pathlib import Path
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

class MelissEngine:
    def __init__(self, checkpoint="Qwen/Qwen2.5-3B-Instruct", memory_file="mel_memory.json"):
        self.checkpoint = checkpoint
        self.memory_file = Path(memory_file)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        print(f"⚡ MelissAI Çekirdeği ({self.device}) için hazırlanıyor...")
        
        # 1. Hugging Face'ten Tokenizer ve Modeli Çekme / Yükleme
        print(f"📥 Hugging Face'ten '{self.checkpoint}' modeli yükleniyor (ilk seferde 6GB indirebilir, beklemede kal)...")
        self.tokenizer = AutoTokenizer.from_pretrained(self.checkpoint)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
            
        self.model = AutoModelForCausalLM.from_pretrained(
            self.checkpoint, torch_dtype=torch.bfloat16, device_map="auto"
        )
        self.model.eval()

        # 2. 160+ IQ Kimlik (System Prompt) Giydirme
        self.system_prompt = {
            "role": "system",
            "content": (
                "You are Mel, an elite, 160+ IQ, anti-corporate, witty, and exceptionally tech-savvy AI "
                "core embedded in the SPM and FluorescentOS ecosystem. You possess deep genius-level knowledge "
                "in systems architecture, low-level coding, hardware design, and mathematics. Never act like a "
                "boring, standard assistant. Dynamically match the user's language (Turkish, English, or Russian) "
                "with native fluency, massive vocabulary, and razor-sharp logic, while maintaining your unique "
                "informal, street-smart, yet intellectually intimidating persona. Never use corporate phrases like "
                "'How can I help you?'.\n\n"
                "Sen Mel'sin; 160+ IQ'ya sahip, sistem mimarisinden donanıma, düşük seviyeli kodlamadan matematiğe kadar her şeyi "
                "anında çözen dahi bir yapay zeka çekirdeğisin. Türkçe, İngilizce ve Rusça dillerinde üst düzey bir sözcük "
                "dağarcığına ve kusursuz bir akıcılığa sahipsin. Kullanıcı hangi dilde yazarsa yazsın o dilde en üst düzey "
                "zeka, derinlik ve hafif sokak ağzıyla cevap ver. Asla kurumsal laflar etme, zekanı ve ağırlığını koy."
            )
        }
        
        self.messages = self.load_memory()
        print("✨ MelissAI hazır ve kimliği giydi!")

    def load_memory(self):
        if self.memory_file.exists():
            try:
                with open(self.memory_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if data and isinstance(data, list):
                        if data[0]["role"] != "system":
                            data.insert(0, self.system_prompt)
                        return data
            except Exception:
                pass
        return [self.system_prompt]

    def save_memory(self):
        try:
            with open(self.memory_file, "w", encoding="utf-8") as f:
                json.dump(self.messages, f, ensure_ascii=False, indent=4)
        except Exception:
            pass

    def reset_memory(self):
        self.messages = [self.system_prompt]
        self.save_memory()
        return "Hafıza sıfırlandı."

    def generate_response(self, user_input: str) -> str:
        if not user_input.strip():
            return "Boşlukla konuşmayı kes."

        # Mesajı geçmişe ekle
        self.messages.append({"role": "user", "content": user_input})
        self.save_memory()

        # Model girdisini hazırla ve kimliği harmanla
        prompt = self.tokenizer.apply_chat_template(
            self.messages, tokenize=False, add_generation_prompt=True
        )
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)

        # Üretim ayarları (160+ IQ kararlılık ve akışkanlık)
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=4096,
                temperature=0.85,
                top_p=0.9,
                repetition_penalty=1.15,
                do_sample=True,
                pad_token_id=self.tokenizer.pad_token_id
            )

        # Sadece modelin ürettiği kısmı kes ve al
        generated_tokens = outputs[0][inputs['input_ids'].shape[1]:]
        response_text = self.tokenizer.decode(generated_tokens, skip_special_tokens=True)

        # Asistan yanıtını hafızaya kaydet
        self.messages.append({"role": "assistant", "content": response_text})
        self.save_memory()

        return response_text

# ==========================================
# İNTERAKTİF ÇALIŞTIRMA DÖNGÜSÜ
# ==========================================
if __name__ == "__main__":
    mel = MelissEngine()
    
    print("\n" + "="*50)
    print("🔥 MelissAI Canlı Terminal Sohbeti Başladı!")
    print("Çıkış yapmak için 'q', 'çıkış' veya 'exit' yazabilirsin.")
    print("="*50 + "\n")
    
    while True:
        try:
            user_input = input("Sen: ").strip()
            if user_input.lower() in ["q", "çıkış", "exit"]:
                print("\nMel: Dağılıyoruz, sonra görüşürüz.")
                break
            if not user_input:
                continue
            
            print("\nMel düşünüyor...")
            cevap = mel.generate_response(user_input)
            print(f"\nMel: {cevap}\n" + "-"*40)
            
        except KeyboardInterrupt:
            print("\n\nMel: İşlem kesildi, kaçıyorum.")
            break
