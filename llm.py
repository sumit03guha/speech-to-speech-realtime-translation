from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI

translation_template = """
Translate the following sentence into {language}, return ONLY the translation, and nothing else.

Sentence: {sentence}
"""

output_parser = StrOutputParser()
llm = ChatOpenAI(temperature=0.0, model="gpt-4o-2024-11-20")
translation_prompt = ChatPromptTemplate.from_template(translation_template)

translation_chain = (
    {"language": RunnablePassthrough(), "sentence": RunnablePassthrough()}
    | translation_prompt
    | llm
    | output_parser
)


def translate(sentence, language):
    data_input = {"language": language, "sentence": sentence}
    translation = translation_chain.invoke(data_input)
    return translation


if __name__ == "__main__":
    print(translate("Hello world!"))
