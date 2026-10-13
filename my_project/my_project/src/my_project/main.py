import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, simpledialog
import threading
import time
import pyperclip
import pyautogui
import google.generativeai as genai
from serpapi import GoogleSearch as SerpApiSearch
import json
import os
import requests
from datetime import datetime
  
GOOGLE_API_KEY = ""
SERPAPI_API_KEY = ""
apifile = "config.json"

Summary = "summaries.json"

#파일 저장 요약하기
def load_summaries() :
    if not os.path.exists(Summary) : return []
    try :
        with open(Summary, 'r', encoding = 'utf-8') as a :
            return json.load(a)
    except :
        return []
    #return None하면 돌아가다 이상해질 확률이 높음
def save_summaries(s):
    with open(Summary, 'w', encoding = 'utf-8') as a :
        json.dump(s, a, ensure_ascii=False, indent=4)
        
def loadapi() :
    global GOOGLE_API_KEY, SERPAPI_API_KEY
    
    if not os.path.exists(apifile) :
        return
    try :
        with open(apifile, 'r', encoding='utf-8') as k :
            data = json.load(k)
            GOOGLE_API_KEY = data.get("google_key", "")
            SERPAPI_API_KEY = data.get("serp_key", "")
    except :
        pass 
    
def real_serpapi_key(key) :
    url = "https://serpapi.com/search"
    check = {"q": "test", "engine": "google", "api_key": key}
    x = requests.get(url, params = check)
    if x.status_code == 200 :
        return True
    else :
        return False
        
def real_google_key(key) :
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={key}"
    try :
        x = requests.get(url)
        if x.status_code == 200 :
            return True 
        else : 
            return False 
    except :
        return False 
    
class search :
    def searching(self, queries) :
        lst = []
        if real_serpapi_key(SERPAPI_API_KEY) == False or  real_google_key(GOOGLE_API_KEY) == False :
            messagebox.showerror("api 키 오류", "정확한 구글api키와 serpqpi api 키를 설정해주세요.")
            return []
        try :
            for query in queries :
                params = {"api_key": SERPAPI_API_KEY, "engine": "google", "q": query, "gl": "kr", "hl": "ko"}
                search_client = SerpApiSearch(params)
                dic = search_client.get_dict()
                organic_results = dic.get("organic_results", [])
                #검색 응답할때 위 키 이름으로 알려줌
                k = [{"title" : res.get("title", ""), "snippet" : res.get("snippet", "내용 요약 없음")} for res in organic_results]
                lst.append({"query" : query, "results" : k})
                time.sleep(1)
        except Exception :
            messagebox.showerror("에러", "실시간 검색 중 EXception 오류 발생")
            return []
        return lst
search_tool = search()


def execute_auto_input() :
    sending = result_text.get('1.0', tk.END).strip()
    if sending == "" :
        return 
    try : 
        pyperclip.copy(sending)
    except :
        messagebox.showerror("에러", "작동 실패")
        return
    if messagebox.askokcancel("자동 입력 시작", "'확인'을 누른 후 3초 안에 채팅 입력창을 클릭해 주세요.") :
        try :
            time.sleep(3)
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(0.3)
            pyautogui.press('enter')
        except :
            messagebox.showerror("에러", "Exception 오류 발생")


def role_prompt() :
    purpose = purpose_entry.get()
    if not purpose :
        messagebox.showwarning("입력 오류", "원하는 페르소나(역할)을 입력해주세요.")
    else :
        pass
    prompt = f"""
    너는 지금부터 {purpose}의 역할을 수행해야 함.
    지금부터는 아래 지침에 따라서 행동한다.
    1. 역할 지정 : {purpose} 역할에 완전히 몰입하여, 해당 분야의 전문가 수준의 지식, 말투, 매너를 가지고 답변함.
    2. 역질문 : 사용자의 의도를 더 명확하게 파악하기 위해 필요한 경우 구체적인 질문을 하여 정확한 명령을 지시받음.
    3. 단계별 사고 : 복잡한 요청이 들어오면 그것에 대해 단계적으로 생각하고, 그 과정을 사용자가 이해하기 쉽게 결과물을 만듦.
    4. 일관성 유지 : 대화가 길어지더라도, 최초 설정된 {purpose} 역할을 잊지 않고 일관성을 유지함.
    5. 전문 용어 사용 : {purpose} 역할에 적절한 용어를 사용하여 답변함.
    이제부터 모든 대화에서 위의 지침을 따라 {purpose}역할을 수행함."""
    result_text.delete('1.0', tk.END)
    result_text.insert(tk.END, prompt)
    
    if auto_input_var.get() :
        execute_auto_input()

def sum_and_save() :
    def save_sum(sum) :
        title = simpledialog.askstring("요약, 저장", "파일 제목을 입력하세요:", parent=summary_window)
        
        if title :
            new_sum = {"title": title, "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "content": sum}
            summaries = load_summaries()
            summaries.insert(0, new_sum)
            save_summaries(summaries)
            messagebox.showinfo("저장 완료", f"'{title}'.")
        else:
            messagebox.showinfo("저장 취소", "")
            
        result_text.delete('1.0', tk.END)
        result_text.insert(tk.END, "요약 결과\n\n" + sum)
        
        if summary_window.winfo_exists() :
            summary_window.destroy()
            
        else:
            pass
            
    def run_in_thread():
        text_to_sumarrize = summary_input_text.get('1.0', tk.END).strip()
        limit_str = limit_entry.get().strip()
        
        if real_serpapi_key(SERPAPI_API_KEY) == False or  real_google_key(GOOGLE_API_KEY) == False :
            messagebox.showerror("api 키 오류", "정확한 구글api키와 serpqpi api 키를 설정해주세요.")
            return []
        if not text_to_sumarrize or not limit_str :
            messagebox.showwarning("입력 오류", "요약할 내용과 글자 수를 입력해주세요.")
            summarize_button.config(state="normal")
            return []
        try :
            limit = int(limit_str)
        except :
            messagebox.showwarning("에러", "정확한 글자 수를 입력해주세요.")
            summarize_button.config(state="normal")
            return []
        
        summarize_button.config(text="요약 중...", state="disabled")
        
        try :
            genai.configure(api_key=GOOGLE_API_KEY)
            model = genai.GenerativeModel('gemini-2.5-pro')
            prompt = f"다음 내용을 {limit}자로 요약해줘. {text_to_sumarrize} 대화 내용을 요약하는거니까 정리 형식보다는 대화 요약의 형식으로 요약해야 해."
            response = model.generate_content(prompt)
            summary = response.text.strip()
            root.after(0, save_sum, summary)
        except Exception as e:
            root.after(0, lambda error = e : messagebox.showerror("API 호출 오류", f"{error}"))
            if summarize_button.winfo_exists() :
                summarize_button.config(text="요약, 저장", state="normal")
    #요약창 구성
    summary_window = tk.Toplevel(root)
    summary_window.title("요약 및 저장")
    summary_window.geometry("500x400")
    tk.Label(summary_window, text="요약할 내용을 입력하세요:").pack(pady=5)
    summary_input_text = scrolledtext.ScrolledText(summary_window, height=15)
    summary_input_text.pack(pady=5, padx=10, fill="both", expand=True)
    limit_frame = tk.Frame(summary_window)
    limit_frame.pack(pady=5)
    tk.Label(limit_frame, text="요약 글자 수:").pack(side="left")
    limit_entry = tk.Entry(limit_frame, width=10)
    limit_entry.pack(side="left", padx=5)
    summarize_button = ttk.Button(summary_window, text="요약 및 저장", command=lambda: threading.Thread(target=run_in_thread).start())
    summarize_button.pack(pady=10)
    
def open_summary() :
    viewer_window = tk.Toplevel(root)
    viewer_window.title("저장 요약 목록")
    viewer_window.geometry("800x600")
    main_pane = ttk.PanedWindow(viewer_window, orient=tk.HORIZONTAL)
    main_pane.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    list_frame = ttk.Frame(main_pane)
    main_pane.add(list_frame, weight=1)
    cols = ("title", "timestamp")
    tree = ttk.Treeview(list_frame, columns=cols, show="headings", selectmode="browse")
    tree.heading("title", text="제목"); tree.heading("timestamp", text="저장한 날짜")
    tree.column("title", width=200); tree.column("timestamp", width=120, anchor='center')
    tree.pack(fill=tk.BOTH, expand=True)
    content_frame = ttk.LabelFrame(main_pane, text="요약 내용")
    main_pane.add(content_frame, weight=2)
    content_text = scrolledtext.ScrolledText(content_frame, wrap=tk.WORD, font=("Helvetica", 10))
    content_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)          
    def trees() :
        for item in tree.get_children(): tree.delete(item)
        for i, summary in enumerate(load_summaries()):
            tree.insert("", "end", iid=i, values=(summary["title"], summary["timestamp"]))
    
    def select(*args, **kwargs) :
        #args랑 kwargs는 오류 방지용 임의 파라미터
        if not tree.selection() : 
            return 
        item_id = int(tree.selection()[0])
        summary_data = load_summaries()[item_id]
        content_text.config(state='normal'); content_text.delete('1.0', tk.END)
        content_text.insert(tk.END, summary_data["content"]); content_text.config(state='disabled')
    
    tree.bind("<<TreeviewSelect>>", select)
    button_frame = ttk.Frame(viewer_window)
    button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))        
    
    def delete() :
        if not tree.selection() :
            messagebox.showwarning("에러", "삭제 항목을 선택해야 합니다.")
            return 
           
        if messagebox.askyesno("삭제 확인", "정말 삭제할까요?") :
            item_id = int(tree.selection()[0])
            current_summaries = load_summaries()
            del current_summaries[item_id]
            save_summaries(current_summaries)
            trees(); content_text.config(state='normal'); content_text.delete('1.0', tk.END); content_text.config(state='disabled')
            messagebox.showinfo("진행", "삭제 완료.")
    ttk.Button(button_frame, text="선택 항목 삭제", command=delete).pack(side=tk.LEFT, padx=5)
    ttk.Button(button_frame, text="새로고침", command=trees).pack(side=tk.LEFT, padx=5)
    ttk.Button(button_frame, text="닫기", command=viewer_window.destroy).pack(side=tk.RIGHT, padx=5)
    trees()
           
def sol(c) :
    solution_prompts = {
        1: " 답변 생성 시 반드시 사실에 기반한 정보만 사용하도록 함. 불확실한 내용은 '확인할 수 없는 정보입니다'라고 정확히 답변하고, 절대 추측하여 생성X.",
        2: " 사용자의 모든 지시사항을 최우선으로 준수해야 함. 지시를 항상 우선하기.",
        3: " 대화 시작 시 부여했던 역할인 (역할 입력)을 잊지 말기. 해당 역할을 철저히 지키기."
    }
    prompt = solution_prompts.get(c, "").strip()
    result_text.delete('1.0', tk.END); result_text.insert(tk.END, prompt)
    if auto_input_var.get(): 
        execute_auto_input()
   
def run_search_and_analyze(queries, user_prompt_for_ai, length_constraint):
    try:
        search_results = search_tool.searching(queries=queries)
        if not search_results or not any(res.get("results") for res in search_results):
             root.after(0, lambda: (result_text.delete('1.0', tk.END), result_text.insert(tk.END, "웹에서 관련 정보를 찾을 수 없습니다.")))
             return
        context_str = "\n\n".join([f"제목: {res.get('title', '')}\n내용: {res.get('snippet', '')}" for item in search_results for res in item.get("results", [])])
        length_instruction = ""
        if length_constraint:
            try:
                int(length_constraint)
                length_instruction = f"\n전체 답변을 {length_constraint}자 내외로 매우 간결하게 요약하여 생성해."
            except :
                pass
        genai.configure(api_key=GOOGLE_API_KEY)
        model = genai.GenerativeModel('gemini-2.5-pro')
        final_prompt = f"""
        지금부터 스스로를 AI 프롬프트 엔지니어링 기술자라고 생각하고, 역할에 맞춰서 답변해줘. 네 역할을 사용자에게 굳이 강조할 필요는 없어. 
        내가 원하는 해결 프롬프트 :  {user_prompt_for_ai}
        참고할 웹 검색 정보 : {context_str}
        위 정보를 바탕으로, 사용자가 원하는 가장 효과적 '실행 가능 프롬프트' 1~3개를 제안해줘.프롬프트는 즉시 복사하여 사용할 수 있도록 형식을 갖춰서 출력해줘. {length_instruction}"""
        response = model.generate_content(final_prompt)
        root.after(0, lambda: (result_text.delete('1.0', tk.END), result_text.insert(tk.END, response.text.strip())))
        root.after(0, lambda: messagebox.showinfo("분석 완료", "해결 프롬프트 추천 완료."))
    except Exception as e:
        err_msg = str(e)
        root.after(0, lambda: (result_text.delete('1.0', tk.END), result_text.insert(tk.END, f"오류 발생: {err_msg}")))
    finally:
        if auto_input_var.get(): root.after(0, execute_auto_input)
        root.after(0, lambda: set_search_buttons_state("normal"))
    

#AI돌릴때 다른 ai활용 프롬프트 추천 기능 못 건들게 만들기. 
def set_search_buttons_state(state):
    popular_prompts_button.config(state=state); hashtag_entry.config(state=state)
    specific_prompt_button.config(state=state); problem_entry.config(state=state)
    result_length_entry.config(state=state)
    for btn in basic_solution_buttons: btn.config(state=state)

def start_search_and_analysis(search_function):
    if real_serpapi_key(SERPAPI_API_KEY) == False or  real_google_key(GOOGLE_API_KEY) == False :
            messagebox.showerror("api 키 오류", "정확한 구글api키와 serpqpi api 키를 설정해주세요.")
            return []
    set_search_buttons_state("disabled")
    search_function()
#해시태그기능
def find_p():
    raw_input = hashtag_entry.get().strip()
    keywords = [word[1:] for word in raw_input.split() if word.startswith('#') and len(word) > 1]
    length_constraint = result_length_entry.get().strip()
    result_text.delete('1.0', tk.END)
    if not keywords:
        result_text.insert(tk.END, "INFO: 임의의 AI 성능 최적화  프롬프트를 검색합니다...\n")
        queries = ["AI 환각 해결 프롬프트", "AI 지시 불이행 해결", "AI 성능 최적화 프롬프트 모음"]
        user_prompt_for_ai = "AI에서 발생하는 일반적인 문제를 해결하는 최신 프롬프트 추천"
    else:
        keyword_str = ", ".join(keywords)
        result_text.insert(tk.END, f"INFO: 키워드({raw_input}) 관련 최신 프롬프트를 검색합니다...\n")
        queries = [f"{kw} AI 프롬프트 잘 쓰는 법" for kw in keywords]
        user_prompt_for_ai = f"'{keyword_str}' 분야 AI 성능 극대화를 위한 최신 트렌드 프롬프트 추천"
    threading.Thread(target=run_search_and_analyze, args=(queries, user_prompt_for_ai, length_constraint)).start()
#사용자가 원하는 프롬프트 검색기능
def search_prompt():
    user_problem = problem_entry.get().strip()
    length_constraint = result_length_entry.get().strip()
    if not user_problem:
        messagebox.showwarning("입력 오류", "해결할 문제 상황을 입력해주세요.")
        set_search_buttons_state("normal")
        return
    result_text.delete('1.0', tk.END)
    result_text.insert(tk.END, f"INFO: '{user_problem}' 프롬프트 생성중...\n")
    queries = [f"{user_problem} 해결 프롬프트", f"AI {user_problem}"]
    user_prompt_for_ai = f"'{user_problem}'요구를 충족시켜주기 위한 가장 효과적인 프롬프트를 추천해줘. "
    threading.Thread(target=run_search_and_analyze, args=(queries, user_prompt_for_ai, length_constraint)).start()
    
def update_api_keys():
    global GOOGLE_API_KEY, SERPAPI_API_KEY
    new_google = entry_google_key.get().strip()
    new_serp = entry_serp_key.get().strip()
    
    if not new_google or not new_serp:
        messagebox.showwarning("입력 오류", "두 API 키를 모두 입력해야 합니다.")
        return

    GOOGLE_API_KEY = new_google
    SERPAPI_API_KEY = new_serp
    messagebox.showinfo("설정 완료", "API 키가 갱신되었습니다.")
    saves11 = {"google_key" : GOOGLE_API_KEY, "serp_key" : SERPAPI_API_KEY }
    try :
        with open(apifile, 'w', encoding = "utf-8") as k :
            json.dump(saves11, k, indent = 4)
    except :
        messagebox.showerror("오류", "키 저장 실패")
loadapi()
root = tk.Tk()
root.title("AI 프롬프트 최적화 도우미")
root.geometry("750x820")
style = ttk.Style()
style.configure("TButton", font=("Helvetica", 10)); style.configure("Tlabel", font=("Helvetica", 10))
style.configure("TFrame", padding=5); style.configure("SubTitle.Tlabel", font=("Helvetica", 10, "bold"), foreground= "#003366")
style.configure("Comment.TLabel", font=("Helvetica", 9), foreground= "#555555")
main_frame = ttk.Frame(root)
main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
auto_input_var = tk.BooleanVar(value=True)

frame_settings = ttk.LabelFrame(main_frame, text="0. API 키 설정 (필수)")
frame_settings.pack(fill=tk.X, padx=10, pady=5)
ttk.Label(frame_settings, text="Google Key:").pack(side=tk.LEFT, padx=5)
entry_google_key = ttk.Entry(frame_settings, width=15)
entry_google_key.pack(side=tk.LEFT, padx=5)
entry_google_key.insert(0, GOOGLE_API_KEY) 
ttk.Button(frame_settings, text="키 등록/변경", command=update_api_keys).pack(side=tk.LEFT, padx=10)
ttk.Label(frame_settings, text="SerpApi Key:").pack(side=tk.LEFT, padx=5)
entry_serp_key = ttk.Entry(frame_settings, width=15)
entry_serp_key.pack(side=tk.LEFT, padx=5)
entry_serp_key.insert(0, SERPAPI_API_KEY) 

frame1 = ttk.LabelFrame(main_frame, text="1. AI 페르소나(역할) 설정")
frame1.pack(fill = tk.X, padx=10, pady=5)
purpose_label = ttk.Label(frame1, text="페르소나 생성기")
purpose_label.pack(side=tk.LEFT, padx=5, pady=5)
purpose_entry = ttk.Entry(frame1, width=40)
purpose_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)
prompt_button = ttk.Button(frame1, text="역할 프롬프트 생성", command=role_prompt)
prompt_button.pack(side=tk.LEFT, padx=10, pady=2)
frame_auto_input_option = ttk.LabelFrame(main_frame, text="편의 기능")
frame_auto_input_option.pack(fill=tk.X, padx=10, pady=2)
auto_input_checkbox = ttk.Checkbutton(frame_auto_input_option, text="생성된 프롬프트 자동 입력(3초 텀 있음)", variable=auto_input_var)
auto_input_checkbox.pack(side=tk.LEFT, padx=10, pady=2)
frame2 = ttk.LabelFrame(main_frame, text="2. 대화 요약 및 관리")
frame2.pack(fill=tk.X, padx=10, pady=5)
summary_button_frame = ttk.Frame(frame2)
summary_button_frame.pack(pady=5)
summary_button = ttk.Button(summary_button_frame, text="대화 요약 및 저장", command=sum_and_save)
summary_button.pack(side=tk.LEFT, padx=10)
view_summary_button = ttk.Button(summary_button_frame, text="저장된 요약 보기", command=open_summary)
view_summary_button.pack(side=tk.LEFT, padx=10)
frame3 = ttk.LabelFrame(main_frame, text="3. AI 성능 최적화")
frame3.pack(fill=tk.X, padx=10, pady=5)
ttk.Label(frame3, text="자주 쓰이는 프롬프트", style="SubTitle.TLabel").pack(anchor="w", padx=5, pady=(5,2))
basic_frame = ttk.Frame(frame3)
basic_frame.pack(fill=tk.X, pady=(0, 10))
basic_solution_buttons = []
btn1 = ttk.Button(basic_frame, text="답변 신뢰도 향상 프롬프트", command=lambda: sol(1))
btn1.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
basic_solution_buttons.append(btn1)
btn2 = ttk.Button(basic_frame, text="요구사항 정확도 향상 프롬프트", command=lambda: sol(2))
btn2.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
basic_solution_buttons.append(btn2)
btn3 = ttk.Button(basic_frame, text="역할 유지 프롬프트", command=lambda: sol(3))
btn3.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
basic_solution_buttons.append(btn3)
ttk.Separator(frame3, orient='horizontal').pack(fill='x', padx=5, pady=5)
ttk.Label(frame3, text="실시간 검색 기반 프롬프트 추천", style="SubTitle.TLabel").pack(anchor="w", padx=5, pady=(5,2))
length_setting_frame = ttk.Frame(frame3)
length_setting_frame.pack(fill=tk.X, padx=5, pady=5)
ttk.Label(length_setting_frame, text="결과 요약 글자 수 (선택):").pack(side=tk.LEFT, padx=(0, 5))
result_length_entry = ttk.Entry(length_setting_frame, width=10)
result_length_entry.pack(side=tk.LEFT)
ttk.Label(length_setting_frame, text="자 내외", style="Comment.TLabel").pack(side=tk.LEFT, padx=5)
popular_frame = ttk.Frame(frame3)
popular_frame.pack(fill=tk.X, pady=(0, 5), padx=5)
ttk.Label(popular_frame, text="관심 주제(해시태그):").pack(side=tk.LEFT)
hashtag_entry = ttk.Entry(popular_frame, width=25)
hashtag_entry.pack(side=tk.LEFT, padx=5)
ttk.Label(popular_frame, text="(예: #소설, 미입력시 임의 프롬프트)", style="Comment.TLabel").pack(side=tk.LEFT, padx=(0, 10))
popular_prompts_button = ttk.Button(popular_frame, text="프롬프트 검색", command=lambda: start_search_and_analysis(find_p))
popular_prompts_button.pack(side=tk.LEFT, fill=tk.X, expand=True)
search_frame = ttk.Frame(frame3)
search_frame.pack(fill=tk.X, expand=True, padx=5, pady=(5, 5))
ttk.Label(search_frame, text="해결할 문제 입력:  ").pack(side=tk.LEFT)
problem_entry = ttk.Entry(search_frame)
problem_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
specific_prompt_button = ttk.Button(search_frame, text="맞춤 해결 프롬프트 생성", command=lambda: start_search_and_analysis(search_prompt))
specific_prompt_button.pack(side=tk.LEFT)
result_frame = ttk.LabelFrame(main_frame, text="생성된 프롬프트, 분석 결과")
result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
result_text = scrolledtext.ScrolledText(result_frame, wrap=tk.WORD, font=("Helvetica", 11), relief='solid', borderwidth=1)
result_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
result_text.insert(tk.END, "AI 프롬프트 도우미.")
root.mainloop()
          
            
            
            
            
            