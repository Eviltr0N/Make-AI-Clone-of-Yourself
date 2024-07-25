from langchain_community.chat_models import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
class LLM:
    def __init__(self, model='llama3', temp=0.3, top_k=40, max_tokens=128):
        self.llm =  ChatOllama(
            model = model,
            keep_alive=-1,
            temperature=temp,
            num_predict = max_tokens,
            top_k = top_k,
            # top_p = 0.9
        )
        self.chat_history = []
        self.max_chat_history = 20 + 20
        self.prompt_template = ChatPromptTemplate.from_messages(
            [
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
            ]
        )
        self.chain = self.prompt_template | self.llm | StrOutputParser()
    def chat(self, prompt):
        self.res = self.chain.invoke({"input": prompt, "chat_history": self.chat_history})
        self.chat_history.append(HumanMessage(content=prompt))
        self.chat_history.append(AIMessage(content=self.res))
        if len(self.chat_history) > self.max_chat_history:
            self.chat_history.pop(0)
            self.chat_history.pop(1)
        # print(len(self.chat_history))
        return self.res
def testing():
    ml = LLM("my_model", 0.4, 40, 128)
    while True:
        question = input("You: ")
        if question == "done":
            return
        print(ml.chat(question))
if __name__ == "__main__":
    testing()