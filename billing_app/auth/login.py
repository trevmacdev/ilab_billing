
import gradio as gr

def login_btn(usr, pwd):
    # Dummy auth: admin/admin => admin role, user/user => user role
    if usr == "admin" and pwd == "admin":
        return (
            gr.update(visible=False),  # pnl_login
            gr.update(visible=True),   # pnl_admin
            gr.update(visible=False),  # pnl_user
            "admin"                    # ROLE value
        )
    elif usr == "user" and pwd == "user":
        return (
            gr.update(visible=False),  # pnl_login
            gr.update(visible=False),  # pnl_admin
            gr.update(visible=True),   # pnl_user
            "user"                     # ROLE value
        )
    return (
        gr.update(visible=True),   # pnl_login
        gr.update(visible=False),  # pnl_admin
        gr.update(visible=False),  # pnl_user
        None                       # ROLE value
    )

def build_login(parent, pnl_admin, pnl_user, ROLE):
    with parent:
        gr.Markdown("## Login")
        tb_usr = gr.Textbox(label="Username", placeholder="Enter username")
        tb_pwd = gr.Textbox(label="Password", type="password", placeholder="Enter password")
        btn_login = gr.Button("Login")
        msg = gr.Markdown(visible=False)  # optional message area

    btn_login.click(
        fn=login_btn,
        inputs=[tb_usr, tb_pwd],
        outputs=[parent, pnl_admin, pnl_user, ROLE],
    )

    return {
        "tb_usr": tb_usr,
        "tb_pwd": tb_pwd,
        "btn_login": btn_login,
        "msg": msg,
    }
