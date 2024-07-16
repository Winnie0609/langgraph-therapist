import streamlit as st
from graph import invoke_agent

st.set_page_config(page_title="AI therapist", layout="centered")


def main():
    st.title("💬 AI therapist with langGraph")
    st.caption("🚀 An AI therapist chatbot powered by OpenAI")

    if "messages" not in st.session_state:
        st.session_state["messages"] = [
            {
                "role": "ai",
                "content": "Is there something you want to discuss or need help with lately?",
            },
        ]

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])
        if msg.get("info"):
            with st.expander("More info"):
                st.json(msg["info"])

    if prompt := st.chat_input():
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)

        # print("----------------------------------")
        # print("conversation", st.session_state["messages"])
        conversation_without_info = [
            {k: v for k, v in msg.items() if k != "info"}
            for msg in st.session_state["messages"]
        ]
        response = invoke_agent(conversation_without_info)
        print("[response from agent]", response)
        print("----------------------------------")
        # reply = response["suggest_reply"]
        reply = response["reply"]
        selected_info = [
            "current_stage",
            "selected_intention",
            "selected_skill",
            "suggestion",
            "feedback",
        ]

        info = {key: value for key, value in response.items() if key in selected_info}
        st.session_state.messages.append({"role": "ai", "content": reply, "info": info})
        st.chat_message("ai").write(reply)

        # print("current [info]", info)
        with st.expander("More info"):
            st.json(info)

        # print("----------------------------------")
        # print("[updated conversation]", st.session_state.messages)


if __name__ == "__main__":
    main()
