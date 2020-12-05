from functools import reduce

# Lam 함수, App 함수
# reduce 함수를 활용하여 리스트로 계속 중첩되어서 받아옴
def Lam(*args):
    if isinstance(args[0], list):
        main_args = [a for a in args[0]]
        main_args.append(args[1])
        rev = reversed(main_args)
    else:
        rev = reversed(args)
    return (reduce(lambda x, y: ['_Lam', y, x], rev))

def App(*args):
    return (reduce(lambda x, y: ['_App', x, y], args))

# ppLamExp_for_succ 함수 , ppLamExp_for_one함수
# Lam, App함수의 반환값인 리스트를 임의로 계속 접근하여 각 지역변수(fianl_app 또는 final_lambda)에 bucket_abstr 규칙에 들어맞는 표현으로 바꿈
# 재귀함수로 최대한 짜보려고 했는데 출력결과 확인만을 위해 직접 접근한 점(애초에 직접 접근하고 수정을 위해 리스트로 받음) 양해부탁드립니다. 더욱 공부하겠습니다.

def ppLamExp_for_succ(App):
    if(App[1][2][2][2][2][1][0]=='_App'):
        final_app=str(App[1][2][2][2][2][1][1])+str(App[1][2][2][2][2][1][2])
        App[1][2][2][2][2][1]=final_app
        if (App[1][2][2][2][2][0]== '_App'):
            final_app=str(App[1][2][2][2][2][1])+str(App[1][2][2][2][2][2])
            App[1][2][2][2][2] = final_app
            if(App[1][2][2][2][0]== '_App'):
                if(len(App[1][2][2][2][1])<len(App[1][2][2][2][2])):
                    final_app=str(App[1][2][2][2][1])+"("+str(App[1][2][2][2][2])+")"
                    App[1][2][2][2]=final_app
                    if(App[1][2][2][0]=='_Lam'):
                        final_lambda=str(App[1][2][2][1])
                        App[1][2][2]=final_lambda
                        if(App[1][2][0]=='_Lam'):
                            final_lambda=str(App[1][2][1])+str(App[1][2][2])
                            App[1][2]=final_lambda
                            if(App[1][0]=='_Lam'):
                                final_lambda=str(App[1][1])+str(App[1][2])

    final="L"+final_lambda+"."+final_app
    return final

def ppLamExp_for_one(App):
    if(App[2][2][2][0]=='_App'):
        final_app=str(App[2][2][2][1])+str(App[2][2][2][2])
        App[2][2][2]=final_app
        if (App[2][2][0]== '_Lam'):
            final_lambda=str(App[2][2][1])
            App[2][2]=final_lambda
            if(App[2][0]=='_Lam'):
                final_lambda=str(App[2][1])+str(App[2][2])

    final="L"+final_lambda+"."+final_app
    return final

# ppLamExp_final함수
# succ 람다표현식과 app 람다표현식을 이어줌
# ski translate를 위한 최종 표현식(문자열)을 만들어줌
# 반환값 형태 : (Lnfx.f(nfx))(Lfx.fx) 임

def ppLamExp_final(App):
    a=ppLamExp_for_succ(App)
    b=ppLamExp_for_one(App)
    final="("+a+")("+b+")"
    return final

# convert_bracket_abstr 함수, translate 함수, distribute 함수
# ski변환을 위한 함수들


# convert_bracket_abstr 함수
# bracket_abstraction 규칙에 들어맞기 위해 표기 수정한 함수
# ex. Lnfx->Ln.Lf.Lx 등으로 변환
def convert_bracket_abstr(line):
    is_Lamda = False
    str = ""
    for ch in line:
        if ch == 'L':
            is_Lamda = True # 다음 for문부터는 is_Lamda ture되어 'L변수.'의 형태로 스트링을 붙이게 됨
            continue
        if ch == '.':
            is_Lamda = False
            continue
        if is_Lamda:
            str += "L"+ch+"."
        else:
            str += ch
    return str

# distribute 함수
# bracket_abstraction rule(2,6)에 필요함. 해당 함수 접근 조건은 새로운 lambda term을 또 생성해야할 때임.
def distribute(line):
    stack_abstr = 0
    spl = -1
    for i in range(len(line) - 1):
        if line[i] == '(': # 괄호 pair로 분리
            stack_abstr = stack_abstr+ 1
        if line[i] == ')':
            stack_abstr = stack_abstr - 1
        if stack_abstr == 0:
            spl = i # 짤리는 부분 저장
    if spl == -1:
        return line, ""
    else:
        return line[:spl + 1], line[spl + 1:]


def translate_to_ski(line):
    #1번 규칙
    #길이가 1이면 그대로 반환 ex. x->x
    if len(line) == 1:
        return line

    # 2번 규칙
    if line[0] != 'L':
        new_t1, new_t2 = distribute(line) # new lambda term으로 쪼갬 (계속 돌림 )
        # print("2번확인")
        if line == new_t1:
            return translate_to_ski(line[1:-1])
        return "(" + translate_to_ski(new_t1) + translate_to_ski(new_t2) + ")"

    # 3번 규칙
    # lamda부분 무시하고 app부터 풀기 시작
    lamda_save = line[1]
    line = line[3:] #app_start부분으로 line 재설정

    if (lamda_save in line) == False: #4번이 아님을 증명!
        return "(K" + translate_to_ski(line) + ")"

    # 4번 규칙
    # 위에서부터 돌다가 람다부분 제외하고 다시 len이 1이 되는 경우임. 1번규칙과 다름
    if len(line) == 1:
        return "I"

    # 5번 규칙
    if line[0] == 'L':
        return translate_to_ski("L" + lamda_save + "." + translate_to_ski(line))

    # 6번 규칙
    new_t1, new_t2 = distribute(line)
    if line == new_t1:
        line = line[1:-1]

    new_t1, new_t2 = distribute(line)  # new lambda term으로 쪼갬 (분배법칙과 비슷한 느낌)
    # return str의 형태는 Lx.(yz) -> (S T[Lx.y] T[Lx.z] ) 와 동일하다.
    return "(S" + translate_to_ski("L" + lamda_save + "." + new_t1) + translate_to_ski("L" + lamda_save + "." + new_t2) + ")"



def main():
    print(translate_to_ski(convert_bracket_abstr(ppLamExp_final(App(Lam(['n', 'f', 'x'], App('f', App(App('n', 'f'), 'x'))), Lam(['f', 'x'], App('f', 'x')))))))

if __name__ == "__main__":
    main()
