# インポート
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
import webbrowser
import tempfile

### 関数 ###
# Manualボタン
def manual_func():
    # テキストボックスのデータ消去
    txtbox.delete("1.0","end")
    # テキストボックスへ書込み
    keyword = '''

 $CONTRL RUNTYP=NEBPATH $END
 $NEB OPTMZR=QUICKMIN VIAPNT=.F. $END
 $NEB MORINT=.T. MOLSYM=.F. UNTCRD=ANGS $END
 $NEB NBEADS=15 MAXCYC=500 $END
 $NEB OPTTOL=0.001D+00 QUCKDT=0.2D+00 SPFORC=0.5D+00 $END

 $DATA

 $END

 $DATAPD

 $END

!$DATAV
!$END

'''
    txtbox.insert("1.end", keyword)
          
# 一時ファイルからテキストボックスへ挿入
def temp_read():
    # テキストボックスのデータ消去
    txtbox.delete("1.0","end")
    try:
        # テキストボックスへ書込み
        fp.seek(0)
        txtbox.insert("1.end", fp.read())
        fp.close()  
    except:
        # エラー通知
        messagebox.showerror("Error", "No Temporary File!!")
    
# Autoボタン
def auto_fuc():
    global fp
    # 一時ファイル作成
    fp = tempfile.TemporaryFile(mode = "a+")
    # 反応物のファイル選択
    typ = [("Reactant","*.out"), ("Reactant","*.gam"), ("Reactant","*.log"), ("All Files","*.*")]
    data_path = filedialog.askopenfilename(filetypes = typ)
    
    # データが選択された場合
    if len(data_path) != 0:
        # outputファイルのリスト化
        with open(data_path,"r") as outfile:
            data = outfile.readlines()
        try:
            ##### 入力ファイルのキーワード追加 #####
            # リストから検索文字列の行番号取得
            for linenum, line in enumerate(data):
                if "INPUT CARD>" in line:
                    finalnum = linenum
                    # 検索行を抽出 (＆不要なINPUT CARD>と空白を削除, OPTIMIZEをNEBPATHに置換)
                    words = data[finalnum].replace(" INPUT CARD>", "").replace("RUNTYP=OPTIMIZE", "RUNTYP=NEBPATH").rstrip() + '\n'
                    # $DATA行で終了
                    if words == " $DATA\n":
                        # DATA+3行取得
                        for linenum, line in enumerate(data):
                            if "$DATA" in line:
                                finalnum = linenum
                                # 検索文字列の3行目までを抽出
                                words = data[(finalnum):(finalnum+3)]
                                # 一時ファイルへ書込み
                                fp.write(''' $CONTRL RUNTYP=NEBPATH $END
 $NEB OPTMZR=QUICKMIN VIAPNT=.F. $END
 $NEB MORINT=.T. MOLSYM=.F. UNTCRD=ANGS $END
 $NEB NBEADS=15 MAXCYC=500 $END
 $NEB OPTTOL=0.001D+00 QUCKDT=0.2D+00 SPFORC=0.5D+00 $END

''')
                                for line in words:
                                    fp.write(line.replace(" INPUT CARD>", "").rstrip() + '\n')
                        break
                    else:
                        # 一時ファイルへ書込み
                        for line in words:
                            # 検索文字列がない行で処理を終了
                            if line == None:
                                break
                            else:
                                fp.write(line)
                                    
            ##### 最適化座標1(反応物)追加 #####
            # 変数削除
            del finalnum
            # リストから検索文字列の行番号取得
            for linenum, line in enumerate(data):
                if "COORDINATES OF ALL ATOMS ARE (ANGS)" in line:
                    finalnum = linenum
            # 検検索文字列の3行目から最終行までリスト内要素を抽出
            words = data[(finalnum+3):]
            # 一時ファイルへ書込み
            for line in words:
                # 最初の空行で処理を終了
                if line == "\n":
                    fp.write(" $END\n\n $DATAPD\n")
                    break
                else:
                    fp.write(line)
                        
            ##### 最適化座標2(生成物)追加 #####
            # 変数削除
            del finalnum
            typ = [("Product","*.out"), ("Product","*.gam"), ("Product","*.log"), ("All Files","*.*")]
            data_path = filedialog.askopenfilename(filetypes = typ)
            # データが選択された場合
            if len(data_path) != 0:
                # outputファイルのリスト化
                with open(data_path,"r") as outfile:
                    data = outfile.readlines()
                # リストから検索文字列の行番号取得
                for linenum, line in enumerate(data):
                    if "COORDINATES OF ALL ATOMS ARE (ANGS)" in line:
                        finalnum = linenum
                # 検検索文字列の3行目から最終行までリスト内要素を抽出
                words = data[(finalnum+3):]
                # 一時ファイルへ書込み
                for line in words:
                    # 最初の空行で処理を終了
                    if line == "\n":
                        fp.write(" $END\n\n!$DATAV\n!$END\n")
                        break
                    else:
                        fp.write(line)
                # テキストボックスへ結果の挿入
                temp_read() 
            else:
                # 一時ファイル削除
                fp.close() 
        except:
            # エラー通知
            messagebox.showerror("Error", "No Required Data!!")
            # 一時ファイル削除
            fp.close() 

# Analysisボタン
def analysis_fuc():
    global fp
    # 一時ファイル作成
    fp = tempfile.TemporaryFile(mode = "a+")
    # 反応物のファイル選択
    typ = [("Output File","*.out"), ("Output File","*.gam"), ("Output File","*.log"), ("All Files","*.*")]
    data_path = filedialog.askopenfilename(filetypes = typ)
    
    # データが選択された場合
    if len(data_path) != 0:
        # outputファイルのリスト化
        with open(data_path,"r") as outfile:
            data = outfile.readlines()
        try:
            # Summary抽出
            for linenum, line in enumerate(data):
                if "Exiting NEB_run routine" in line:
                    finalnum = linenum

            # 検索文字列の6行目から最終行までリスト内要素を抽出
            words = data[(finalnum+6):]
            # 一時ファイルへ書込み
            fp.write("          ------------------------------\n          Exiting NEB_run routine\n          ------------------------------\n*** Summary ***\n")
            for line in words:
                # 最初の空行で処理を終了
                if line == "\n":
                    fp.write("\n")
                    break
                else:
                    fp.write(line)
            # 座標抽出
            for linenum, line in enumerate(data):
                if "Chem3D input in cc1 format for a movie" in line:
                    finalnum = linenum

            # 検索文字列から最終行までリスト内要素を抽出
            words = data[(finalnum):]
            # 一時ファイルへ書込み
            for line in words:
                # 最初の空行で処理を終了
                if line == "\n":
                    break
                else:
                    fp.write(line)
            # テキストボックスへ結果の挿入
            temp_read() 
        except:
            # エラー通知
            messagebox.showerror("Error", "No Required Data!!")
            # 一時ファイル削除
            fp.close() 
    else:
        # 一時ファイル削除
        fp.close()        
            
# ファイル保存
def save_file():
    # 保存ダイアログの表示
    typ = [("Input File","*.inp"), ("Text Files","*.txt")] 
    save_path = tk.filedialog.asksaveasfilename(filetypes = typ, defaultextension = "inp")
    
    if len(save_path) != 0:
        # ファイルが選択された場合データを書き込み
        with open(save_path, "w") as file:
            # テキストボックスの値を取得
            data = txtbox.get("1.0", "end")
            file.write(data)
            
# HP(配布ページ)へアクセス
def hp_web():
    hp_url = "http://pc-chem-basics.blog.jp/archives/25967142.html"
    webbrowser.open(hp_url)

# NEB Keywords(キーワードの概要ウインドウ)
def info_window():
    # サブウインドウの作成
    sub_window = tk.Toplevel(root)
    sub_window.resizable(width = False, height = False)
    # フレーム
    sub_frame = ttk.Labelframe(sub_window, text = "  $NEB OPTIONS (Default)  ")
    sub_frame.pack(padx = 10, pady = 10)
    # ラベル
    label = tk.Label(sub_frame, justify = "left", text = '''
 Number of beads                        (NBEADS) = 15
 Spring force constant                  (SPFORC) = 0.50000  (hartree/bohr)
 Optimizer                              (OPTMZR) = QUICKMIN  (or DIISBFGS)
 Via-point structure                    (VIAPNT) = F  (or T  ($DATAVI～$END))
 Transition-state search                (TALOCT) = F
 Unit for coordinates                   (UNTCRD) = ANGS  (or BOHR)
 Maximum cycle number                   (MAXCYC) = 500
 Distance multiplier for quick-min      (QUCKDT) = 0.20000  (bohr)
 Tolerance for geometrical optimization (OPTTOL) = 0.00100  (au/bohr)
 Caution for molecular orientation      (MORINT) = F
 Caution for molecular symmetry         (MOLSYM) = F
 Restart option                         (RESTRT) = F
 Number of the cycles                   (ISTART) = 0
 Parallel computation                   (GOPARR) = T
 
 ''')
    label.pack(padx = 20)
    
### GUI ###
# ウインドウの作成
root = tk.Tk()
root.title("Gnebit Ver.1.0.0")
root.minsize(width=500, height=200)
# フレーム
frame = ttk.Frame(root, padding = 5)
frame.pack(padx = 5, pady = 5, fill = tk.BOTH)
frame1 = ttk.Labelframe(frame, text = "INPUT", padding = 5)
frame1.pack(padx = 5, pady = 5, anchor = tk.W, side = tk.LEFT)
frame2 = ttk.Labelframe(frame, text = "OUTPUT", padding = 5)
frame2.pack(padx = 5, pady = 5, anchor = tk.W, side = tk.LEFT)
frame3 = ttk.Frame(root, padding = 5)
frame3.pack(padx = 5, pady = 5, fill = tk.BOTH, expand =1)
# Manualボタン
manual_button = tk.Button(frame1, text = "Manual", command = manual_func)
manual_button.pack(side = tk.LEFT, padx = 5, pady = 5)
# Autoボタン
auto_button = tk.Button(frame1, text = "Auto", command = auto_fuc)
auto_button.pack(side = tk.LEFT, padx = 5, pady = 5)
# Analysisボタン
auto_button = tk.Button(frame2, text = "Analysis", command = analysis_fuc)
auto_button.pack(side = tk.LEFT, padx = 5, pady = 5)
# テキストボックス
txtbox = tk.Text(frame3, width = 110, height = 30, wrap = "none")
# スクロールバー作成
yscroll = tk.Scrollbar(frame3, orient = tk.VERTICAL, command = txtbox.yview)
txtbox["yscrollcommand"] = yscroll.set
yscroll.pack(side = tk.RIGHT, fill = tk.BOTH)
xscroll = tk.Scrollbar(frame3, orient = tk.HORIZONTAL, command = txtbox.xview)
txtbox["xscrollcommand"] = xscroll.set
xscroll.pack(side = tk.BOTTOM, fill = tk.BOTH)
# テキストボックスの配置
txtbox.pack(fill = tk.BOTH, expand =1)

# メニューバーの作成
menubar = tk.Menu(root)
root.configure(menu = menubar)
# File メニュー
filemenu = tk.Menu(menubar, tearoff = 0)
menubar.add_cascade(label = "File", menu = filemenu)
# File メニューの内容
filemenu.add_command(label = "Save as...", command = save_file)
filemenu.add_separator()
filemenu.add_command(label = "Exit",
command = lambda: root.destroy())
# Help メニュー
helpmenu = tk.Menu(menubar, tearoff = 0)
menubar.add_cascade(label = "Help", menu = helpmenu)
# >NEB Keywords
helpmenu.add_command(label = "NEB Keywords", command = info_window)
helpmenu.add_separator()
# >Manual
helpmenu.add_command(label = "Manual", command = hp_web)

# ウインドウ状態の維持
root.mainloop()