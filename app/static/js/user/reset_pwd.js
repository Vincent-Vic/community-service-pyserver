;

var mod_pwd_ops = {
    init: function () {
        this.eventBind();
    },
    eventBind: function () {
        $("#save").click(function () {
            var btn_target = $(this);
            if (btn_target.hasClass("disabled")) {
                common_ops.alert("正在处理！！请不要重复提交~~");
                return;
            }

            var old_password = $("#old_password").val();
            var new_password = $("#new_password").val();

            if (!old_password) {
                common_ops.alert("请输入原密码~");
                return false;
            }

            if (!new_password || new_password.length < 6) {
                common_ops.alert("请输入不少于6位的新密码~");
                return false;
            }


            //至少6-16个字符，至少1个大写字母，1个小写字母和1个数字
            var loginPwdReg = !!new_password.match( /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[^]{6,16}$/);
            //如果登录密码不能通过验证
            if(!id && loginPwdReg == false){
                common_ops.alert("请输入符合规范的登录密码(至少6-16个字符，至少1个大写字母，1个小写字母和1个数字)~");
                return false;
            }

           // btn_target.addClass("disabled");
            var data = {
                old_password: old_password,
                new_password: new_password
            }

            $.ajax({
                url: common_ops.buildUrl("/user/reset-pwd"),
                type: "POST",
                data: data,
                dataType: "json",
                success: function (res) {
                    //btn_target.removeClass("disabled");
                    var callback = null;
                    if (res.code == 200) {
                        callback = function () {
                            window.location.href = window.location.href;
                        }
                    }
                    common_ops.alert(res.msg, callback);
                },
                error:common_ops.errorHandle
            })

        });
    }
};

$(document).ready(function () {
    mod_pwd_ops.init();
});