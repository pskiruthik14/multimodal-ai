"""
Bilingual & Indian-Language Tutoring Engine (English + Hinglish/Hindi)
Optional Enhancement 6.d: English lectures with Hindi/Hinglish explanations.
"""

from typing import Dict, Any

HINGLISH_CONCEPT_EXPLANATIONS: Dict[str, str] = {
    "topic-1": (
        "**Loss Functions (नुकसान का आकलन):**\n"
        "Machine learning model jab galti karta hai, toh us galti ko calculate karne ke liye hum **Loss Function** ka use karte hain.\n"
        "- **MSE (Mean Squared Error):** Regression problems ke liye use hota hai. Agar prediction door hai, toh square hone ki wajah se penalty bahut badi lagti hai.\n"
        "- **Cross-Entropy Loss:** Classification ke liye best hai kyunki yeh probability distributions ke beech ka gap calculate karta hai. Jab model galat prediction me overconfident hota hai, tab yeh steep gradient deta hai taaki weights jaldi theek ho sakein!"
    ),
    "topic-2": (
        "**Gradient Descent & Adam Optimizer (पहाड़ से नीचे उतरने का तरीका):**\n"
        "Socho aap ek ghane kohre wale pahad (loss surface) par khade hain aur aapko sabse gehre valley (minimum loss) tak pohanchana hai.\n"
        "- **SGD:** Har kadam par thoda darta hai aur idhar-udhar oscillate karta hai.\n"
        "- **Momentum:** Ek bhaari cricket ball ki tarah hai—jo consistent direction me speed pakad leta hai aur choti-moti ravines me nahi phasta.\n"
        "- **Adam Optimizer:** Yeh dono moments (speed aur step size) ko adapt karta hai. Iska bias-correction shuruati iterations me 0-initialization ko compensate karta hai!"
    ),
    "topic-3": (
        "**Backpropagation & Vanishing Gradients (गलतियों से सीखने की चेन):**\n"
        "Neural network me har layer pichli layer par depend karti hai. Jab final output galat aata hai, tab **Chain Rule** ke zariye error ko aakhiri layer se pehli layer tak wapas bheja jata hai.\n"
        "- **Vanishing Gradient problem:** Purane Sigmoid activation function ka derivative maximum 0.25 hota hai. Deep network me multiply hote-hote gradient lagbhag zero ho jata tha.\n"
        "- **ReLU (Rectified Linear Unit):** Isne revolution la diya! Kyunki positive values ke liye iska slope hamesha 1 rehta hai, gradients bina fade huye aasaani se pass ho jate hain."
    ),
    "topic-4": (
        "**Convolutional Neural Networks (Images ko dekhne ka dhang):**\n"
        "Computer image ko pixel grid ki tarah dekhta hai. CNN ek chota sliding filter (kernel) use karta hai jo image ke upar ghoomta hai aur edges, textures, shapes detect karta hai.\n"
        "- **ResNet Skip Connections:** Jab hum network ko bahut deep (100+ layers) banate the, toh training error badh jata tha. ResNet ne ek seedha shortcut link 'x' jodh diya. Isse gradient seedha jump karke piche pohanch jata hai bina kisi loss ke!"
    ),
    "topic-5": (
        "**LSTM & Sequence Modeling (Pichli baatein yaad rakhna):**\n"
        "Normal neural networks me sequence ya memory ka concept nahi hota. Vanilla RNN me purana context jaldi bhool jata hai (gradient vanishing).\n"
        "- **LSTM (Long Short-Term Memory):** Isme ek constant conveyor belt (Cell State C_t) hoti hai. Aur teen gates hote hain:\n"
        "  1. **Forget Gate:** Purani bekar baaton ko delete karta hai.\n"
        "  2. **Input Gate:** Nayi important information ko save karta hai.\n"
        "  3. **Output Gate:** Decide karta hai ki current step par kya output dena hai."
    ),
    "topic-6": (
        "**Transformers & Self-Attention (Attention Is All You Need):**\n"
        "Transformer architecture modern AI (ChatGPT, Gemini) ki backbone hai!\n"
        "- **Self-Attention:** Har word sentence ke baaki saare words ke saath interact karta hai. Q (Query), K (Key), V (Value) vectors ke zariye yeh dhyan deta hai ki kis word ka kiske saath gehra connection hai.\n"
        "- **Positional Encoding:** Kyunki Transformer saare words ko ek saath parallel me process karta hai, isliye words ka sequence order batane ke liye sine aur cosine waves ka positional encoding add kiya jata hai!"
    )
}

class BilingualEngine:
    """Manages bilingual explanations and Indian language adaptations."""

    @staticmethod
    def get_hinglish_explanation(topic_id: str, default_text: str) -> str:
        """Returns Hinglish explanation for topic if available, else wraps with bilingual framing."""
        if topic_id in HINGLISH_CONCEPT_EXPLANATIONS:
            return HINGLISH_CONCEPT_EXPLANATIONS[topic_id]
            
        return (
            "**Bilingual Overview (सरल हिंदी व्याख्या):**\n"
            f"Is topic ka main objective yeh hai ki: {default_text[:300]}...\n\n"
            "Sabhi technical terms aur formulas aapke course materials ke saath cited hain."
        )
