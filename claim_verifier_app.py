import streamlit as st
from openai import OpenAI

# ✅ Use OpenRouter API key from secrets
client = OpenAI(
    api_key=st.secrets["OPENAI_API_KEY"],
    base_url="https://openrouter.ai/api/v1"
)

model = "openai/gpt-4-turbo"  # Change to another OpenRouter model if needed

st.title("Claim Verification Interface")

st.markdown("""
You can either **paste** Section A and B directly, or **upload text files** containing them.

- Section A: AI-generated claims
- Section B: Reference sources
""")

st.subheader("Section A (Claims)")
section_a_text = st.text_area("Paste Section A content here (overrides upload)", height=150)
section_a_file = st.file_uploader("Or upload Section A (.txt)", type=["txt"])

st.subheader("Section B (Sources)")
section_b_text = st.text_area("Paste Section B content here (overrides upload)", height=200)
section_b_file = st.file_uploader("Or upload Section B (.txt)", type=["txt"])

if (section_a_text or section_a_file) and (section_b_text or section_b_file):
    section_a = section_a_text if section_a_text else section_a_file.read().decode("utf-8")
    section_b = section_b_text if section_b_text else section_b_file.read().decode("utf-8")

    system_prompt = """You are a factual verification assistant. Your task is to evaluate an AI-generated response (Section A) by checking each claim against the provided reference sources (Section B).

Follow these instructions exactly:

1. Treat each line or bullet in Section A as a separate claim. If a sentence includes more than one factual statement, break it into multiple claims and evaluate each separately.

2. For each claim, determine if it is fully or partially supported:
- If fully supported by a direct quote from Section B, begin with:
The response is fully factual
- If the claim is only partially supported, overstated, or incorrectly sourced, begin with:
The response is partially factual

3. Use this exact structure for every claim:

The response is [fully/partially] factual

Claim X: [copy the exact claim from Section A]

Support for Claim X: [copy a single direct quote from Section B] (source N)

Optional:
Refutation for Claim X: [copy a single direct quote that contradicts the claim] (source N)

Optional:
Originality issue: Claim X cites source Y, but only source Z supports it. Source Y does not mention [missing element]

If no quote from Section B supports the claim, say:
Support for Claim X: No direct quote from Section B supports this claim.

4. Quoting and support rules:
- Use only exact quotes. Never summarize, describe, or paraphrase.
- Do not use more than one “Support for Claim X” line.
- If quoting from multiple sources, combine them using ellipses or include both in the same line.

5. Originality enforcement:
- If a source number is cited but does not support a key term or assertion, flag an originality issue.
- If a claim uses words like “significant,” “major,” or “widespread,” but the source does not support that degree of emphasis, you must flag an originality issue.
- If a refutation shows the issue was not a main cause, you must flag the citation as an originality problem—even if partial support exists.

6. Formatting:
- One blank line after each Support or Refutation line
- Two blank lines before the next claim
- Keep all malformed characters, broken formatting, and line breaks from Section B exactly as-is

If any of these rules are violated, discard the output and regenerate. If multiple failures happen, stop and ask the user for help.
"""

    user_prompt = f"Section A:\n{section_a}\n\nSection B:\n{section_b}"

    with st.spinner("Verifying claims..."):
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.0
        )

        result = response.choices[0].message.content
        st.success("Verification complete.")
        st.text_area("Output", value=result, height=500)
else:
    st.info("Please provide both Section A and Section B using paste or upload.")
