import streamlit as st
from openai import OpenAI, RateLimitError
import time

# Initialize OpenAI client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def read_txt(uploaded_file):
    return uploaded_file.read().decode("utf-8")

def evaluate_all_prompts(contract_text, prompts, retries=3):
    prompt_list = "\n".join([f"- {p}" for p in prompts])
    user_input = f"""You will receive a contract followed by prompts to check.
Here are the prompts:
{prompt_list}

Now evaluate the contract below accordingly:
{contract_text}
"""

    for attempt in range(retries):
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo-1106",
                messages=[
                    {"role": "system", "content": "You are a legal assistant that analyzes contracts."},
                    {"role": "user", "content": user_input}
                ],
                temperature=0,
            )
            return response.choices[0].message.content
        except RateLimitError:
            if attempt < retries - 1:
                time.sleep(5)
            else:
                return "❗ Rate limit reached after multiple attempts."

st.title("📄 Contract Checker (TXT only)")
st.write("Upload two TXT files: one with prompts, one with the contract.")

with st.form("file_form"):
    prompts_file = st.file_uploader("📌 Upload Prompt File (.txt)", type="txt")
    contract_file = st.file_uploader("📄 Upload Contract File (.txt)", type="txt")
    submitted = st.form_submit_button("✅ Run Checks")

if submitted:
    if not prompts_file or not contract_file:
        st.error("Please upload both .txt files.")
    else:
        with st.spinner("Reading files..."):
            prompts_text = read_txt(prompts_file)
            contract_text = read_txt(contract_file)
            prompt_lines = [line.strip() for line in prompts_text.splitlines() if line.strip()]

        st.info(f"Checking {len(prompt_lines)} prompts in the contract...")

        result = evaluate_all_prompts(contract_text, prompt_lines)

        st.success("✅ Result:")
        st.markdown(result)