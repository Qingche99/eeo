# -*- coding: utf-8 -*-
"""
@Author   : 清澈
@Time     :2026/1/15
@File     :api.py
@IDE      :PyCharm
"""
import json
import requests

from typing import Dict, List, Any, Optional
from .urls import ApiUrls
from .utils import SignatureUtils, RequestUtils


class ClassInAPI:
    """
    ClassIn API客户端

    如果你有任何疑问，可以通过eeoapisupport@eeoa.com联系我们
    If you have any questions you can contact us at eeoapisupport@eeoa.com
    ClassIn APIDoc：https://docs.eeo.cn/api/
    """

    def __init__(self, school_uid: int, school_secret: str, domain: str = 'https://api.eeo.cn'):
        """
        初始化ClassIn API客户端

        Args:
            school_uid: eeo 学校账号UID
            school_secret: 密钥
            domain: API域名，默认为 https://api.eeo.cn
        """
        self.SID = school_uid
        self.secret = school_secret
        self.urls = ApiUrls(domain)
        self.session = requests.Session()

    def _get_safe_key(self) -> tuple:
        """获取安全密钥"""
        return SignatureUtils.generate_safe_key(self.secret)

    def _create_v2_headers(self, payload: Dict[str, Any]) -> Dict[str, str]:
        """
        创建v2接口的请求头

        Args:
            payload: 请求数据

        Returns:
            Dict: 请求头
        """
        return SignatureUtils.generate_v2_signature(payload, self.SID, self.secret)

    def _make_request(self, url: str, **kwargs) -> Dict[str, Any]:
        """
        发送HTTP POST请求

        Args:
            url: 请求URL
            **kwargs: 请求参数

        Returns:
            Dict: 响应数据
        """
        try:
            response = self.session.request('POST', url, **kwargs)
            response.raise_for_status()
            return RequestUtils.validate_response(response)
        except requests.RequestException as e:
            raise Exception(f"请求失败: {e}") from e

    def _make_file_request(self, url: str, data: Dict[str, Any], file_path: str) -> Dict[str, Any]:
        """
        发送带文件的 multipart/form-data POST 请求（文件字段名固定为 Filedata）

        Args:
            url: 请求URL
            data: 表单参数（v1签名字段，不含文件）
            file_path: 本地文件路径

        Returns:
            Dict: 响应数据
        """
        try:
            with open(file_path, 'rb') as f:
                response = self.session.request('POST', url, data=data, files={'Filedata': f})
                response.raise_for_status()
                return RequestUtils.validate_response(response)
        except FileNotFoundError as e:
            raise FileNotFoundError(f"文件不存在: {file_path}") from e
        except requests.RequestException as e:
            raise Exception(f"请求失败: {e}") from e

    # =============== 用户相关接口 ===============

    def register(self, account: str, password: str, nickname: Optional[str] = None,
                 addToSchoolMember: Optional[int] = None,
                 file_path: Optional[str] = None) -> Dict[str, Any]:
        """
        注册用户

        Args:
            account: 用户手机号（格式：00国家号-手机号，中国大陆可省略国家号）或邮箱，二选一
            password: 明文密码，6-20字符（也可用md5pass参数传MD5密码）
            nickname: 用户昵称，最多24字符；首次注册时同步至客户端昵称，非首次注册不修改
            addToSchoolMember: 注册后是否加入机构，0=不加入，1=加为学生，2=加为老师
            file_path: 头像图片本地路径（选填，对应接口参数 Filedata）

        Returns:
            Dict: 响应数据，data=用户UID；errno=135手机已注册（返回UID），461邮箱已注册（返回UID）
        """
        timeStamp, safeKey = self._get_safe_key()

        base_data = {
            'SID': self.SID,
            'timeStamp': timeStamp,
            'safeKey': safeKey,
            'password': password,
            'nickname': nickname,
            'addToSchoolMember': addToSchoolMember
        }

        if '@' in account:
            base_data['email'] = account
        else:
            base_data['telephone'] = account

        data = RequestUtils.prepare_request_data(base_data)
        if file_path:
            return self._make_file_request(self.urls.register, data, file_path)
        return self._make_request(self.urls.register, data=data)

    def register_multiple(self, userJson: List[Dict]) -> Dict[str, Any]:
        """
        批量注册用户（最多10个）

        Args:
            userJson: 用户信息列表，每项包含：
                telephone: 手机号（与email二选一）
                email: 邮箱（与telephone二选一）
                nickname: 昵称，最多24字符（可选）
                password: 明文密码，6-20字符（与md5pass二选一）
                md5pass: MD5密码，32位小写（与password二选一）
                addToSchoolMember: 0=不加入，1=加为学生，2=加为老师（可选）
                customColumn: 自定义标识，1-50字符（可选，用于结果对应）

        Returns:
            Dict: 响应数据，data[]每项含 data（UID）、telephone、customColumn、errno、error
        """
        timeStamp, safeKey = self._get_safe_key()

        data = {
            'SID': self.SID,
            'timeStamp': timeStamp,
            'safeKey': safeKey,
            'userJson': json.dumps(userJson)
        }

        return self._make_request(self.urls.registerMultiple, data=data)

    def modify_password(self, uid: int, oldMd5pass: str, password: Optional[str] = None,
                        md5pass: Optional[str] = None) -> Dict[str, Any]:
        """
        修改用户密码

        Args:
            uid: 用户UID
            oldMd5pass: 原密码的MD5值，32位小写
            password: 新明文密码，6-20字符（与md5pass二选一，都传时以md5pass为准）
            md5pass: 新密码的MD5值，32位小写（与password二选一）

        Returns:
            Dict: 响应数据，errno=1成功
        """
        timeStamp, safeKey = self._get_safe_key()

        payload = {
            'SID': self.SID,
            'timeStamp': timeStamp,
            'safeKey': safeKey,
            'uid': uid,
            'oldMd5pass': oldMd5pass,
            'password': password,
            'md5pass': md5pass,
        }

        data = RequestUtils.prepare_request_data(payload)
        return self._make_request(self.urls.modifyPassword, data=data)

    def add_teacher(self, teacherAccount: str, teacherName: str,
                    file_path: Optional[str] = None) -> Dict[str, Any]:
        """
        添加机构老师

        Args:
            teacherAccount: 老师手机号或邮箱
            teacherName: 老师姓名，1-24字符
            file_path: 头像图片本地路径（选填，对应接口参数 Filedata）

        Returns:
            Dict: 响应数据，data=关系ID（可忽略）；errno=219老师不存在
        """
        timeStamp, safeKey = self._get_safe_key()

        payload = {
            'SID': self.SID,
            'timeStamp': timeStamp,
            'safeKey': safeKey,
            'teacherAccount': teacherAccount,
            'teacherName': teacherName
        }

        if file_path:
            return self._make_file_request(self.urls.addTeacher, payload, file_path)
        return self._make_request(self.urls.addTeacher, data=payload)

    def edit_teacher(self, teacherUid: int, teacherName: str,
                     file_path: Optional[str] = None) -> Dict[str, Any]:
        """
        编辑老师信息

        Args:
            teacherUid: 老师UID
            teacherName: 老师姓名，1-24字符
            file_path: 头像图片本地路径（选填，对应接口参数 Filedata）

        Returns:
            Dict: 响应数据，errno=219老师不存在
        """
        timeStamp, safeKey = self._get_safe_key()

        payload = {
            'SID': self.SID,
            'timeStamp': timeStamp,
            'safeKey': safeKey,
            'teacherUid': teacherUid,
            'teacherName': teacherName
        }

        if file_path:
            return self._make_file_request(self.urls.editTeacher, payload, file_path)
        return self._make_request(self.urls.editTeacher, data=payload)

    def stop_using_teacher(self, teacherUid: int) -> Dict[str, Any]:
        """
        停用老师

        Args:
            teacherUid: 老师UID

        Returns:
            Dict: 响应数据，errno=136机构下无此老师，317有未结束课节无法停用，386机构账号不能停用
        """
        timeStamp, safeKey = self._get_safe_key()

        payload = {
            'SID': self.SID,
            'timeStamp': timeStamp,
            'safeKey': safeKey,
            'teacherUid': teacherUid,
        }

        return self._make_request(self.urls.stopUsingTeacher, data=payload)

    def restart_using_teacher(self, teacherUid: int) -> Dict[str, Any]:
        """
        启用老师

        Args:
            teacherUid: 老师UID

        Returns:
            Dict: 响应数据，errno=136机构下无此老师，800账号已停用
        """
        timeStamp, safeKey = self._get_safe_key()

        payload = {
            'SID': self.SID,
            'timeStamp': timeStamp,
            'safeKey': safeKey,
            'teacherUid': teacherUid,
        }

        return self._make_request(self.urls.restartUsingTeacher, data=payload)

    def add_school_student(self, studentAccount: str, studentName: str) -> Dict[str, Any]:
        """
        添加机构学生

        Args:
            studentAccount: 学生手机号或邮箱
            studentName: 学生姓名，1-24字符

        Returns:
            Dict: 响应数据，errno=113账号未注册，133已是学生，134手机号无效，886账号被停用
        """
        timeStamp, safeKey = self._get_safe_key()

        payload = {
            'SID': self.SID,
            'timeStamp': timeStamp,
            'safeKey': safeKey,
            'studentAccount': studentAccount,
            'studentName': studentName
        }

        return self._make_request(self.urls.addSchoolStudent, data=payload)

    def edit_school_student(self, studentUid: int, studentName: str) -> Dict[str, Any]:
        """
        编辑机构学生信息

        Args:
            studentUid: 学生UID
            studentName: 学生姓名，1-24字符

        Returns:
            Dict: 响应数据，errno=228机构下无此学生
        """
        timeStamp, safeKey = self._get_safe_key()

        payload = {
            'SID': self.SID,
            'timeStamp': timeStamp,
            'safeKey': safeKey,
            'studentUid': studentUid,
            'studentName': studentName
        }

        return self._make_request(self.urls.editSchoolStudent, data=payload)

    def modify_course_student_nickname(self, studentUids: List[int]) -> Dict[str, Any]:
        """
        同步学生班级昵称

        Args:
            studentUids: 学生UID列表，每次最多100个，仅同步未结课班级的班级昵称

        Returns:
            Dict: 响应数据，data数组每项含 studentUid、code、msg
        """
        payload = {'studentUids': studentUids}
        headers = self._create_v2_headers(payload)
        return self._make_request(self.urls.modifyCourseStudentNickName, data=json.dumps(payload), headers=headers)

    def update_class_student_comment(self, classId: int, commentJson: List[Dict]) -> Dict[str, Any]:
        """
        更新课节教师对学生的评价

        Args:
            classId: 课节ID
            commentJson: 评价数据列表，每项包含：
                studentUid: 学生UID
                starNum: 评分星级 0-5
                comment: 评价内容，最长1000字
                customColumn: 自定义标识（选填，1-50字符）

        Returns:
            Dict: 响应数据
        """
        timeStamp, safeKey = self._get_safe_key()

        payload = {
            'SID': self.SID,
            'timeStamp': timeStamp,
            'safeKey': safeKey,
            'classId': classId,
            'commentJson': json.dumps(commentJson)
        }

        return self._make_request(self.urls.updateClassStudentComment, data=payload)

    # =============== 课程相关接口 ===============

    def add_course(self, courseName: str, file_path: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """
        创建课程

        Args:
            courseName: 课程名称，1-90字符
            file_path: 课程封面图片本地路径（选填，对应接口参数 Filedata）
            **kwargs: 其他参数（均为选填）
                folderId: 授权云盘文件夹ID
                expiryTime: 课程过期时间（Unix时间戳，秒），不传或0=永久有效
                mainTeacherUid: 班主任UID
                subjectId: 课程学科分类，0-16或99
                catId: 课程组织架构ID
                courseIntroduce: 课程简介，0-400字符
                classroomSettingId: 教室设置ID
                courseUniqueIdentity: 机构唯一标识，1-32字符（已存在则返回已有课程ID）
                allowAddFriend: 班级成员互加好友，0=不允许，1=允许
                allowStudentModifyNickname: 学生修改班级昵称，0=不允许，1=允许
                notAllowDeleteCourseStudentReplay: 离开班级学生查看权限，0=允许，1=不允许

        Returns:
            Dict: 响应数据，data=课程ID
        """
        timeStamp, safeKey = self._get_safe_key()

        base_data = {
            'SID': self.SID,
            'timeStamp': timeStamp,
            'safeKey': safeKey,
            'courseName': courseName
        }

        data = RequestUtils.prepare_request_data(base_data, **kwargs)
        if file_path:
            return self._make_file_request(self.urls.addCourse, data, file_path)
        return self._make_request(self.urls.addCourse, data=data)

    def edit_course(self, courseId: int, file_path: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """
        编辑课程

        Args:
            courseId: 课程ID
            file_path: 课程封面图片本地路径（选填，对应接口参数 Filedata）
            **kwargs: 其他参数（均为选填，至少传一个）
                courseName: 课程名称，1-40字符
                folderId: 授权云盘文件夹ID
                expiryTime: 课程过期时间（Unix时间戳），0=永不过期，不传=不修改
                mainTeacherUid: 班主任UID
                subjectId: 课程学科分类，0-16或99
                catId: 组织架构ID
                stamp: 是否将班主任加入教师列表，1=加入，2=不加入
                courseIntroduce: 课程简介，0-400字符
                classroomSettingId: 教室设置ID
                allowAddFriend: 班级成员互加好友，0=不允许，1=允许
                allowStudentModifyNickname: 学生修改班级昵称，0=不允许，1=允许
                notAllowDeleteCourseStudentReplay: 离开班级学生查看权限，0=允许，1=不允许

        Returns:
            Dict: 响应数据，errno=144课程不存在，310班主任不存在，371教室设置不存在
        """
        timeStamp, safeKey = self._get_safe_key()

        base_data = {
            'SID': self.SID,
            'timeStamp': timeStamp,
            'safeKey': safeKey,
            'courseId': courseId
        }

        data = RequestUtils.prepare_request_data(base_data, **kwargs)
        if file_path:
            return self._make_file_request(self.urls.editCourse, data, file_path)
        return self._make_request(self.urls.editCourse, data=data)

    def end_course(self, courseId: int) -> Dict[str, Any]:
        """
        结束课程

        Args:
            courseId: 课程ID

        Returns:
            Dict: 响应数据，errno=394课程下有正在进行的课节无法结束
        """
        timeStamp, safeKey = self._get_safe_key()

        payload = {
            'SID': self.SID,
            'timeStamp': timeStamp,
            'safeKey': safeKey,
            'courseId': courseId,
        }

        return self._make_request(self.urls.endCourse, data=payload)

    def add_course_group(self, courseId: int, groupName: str, groupList: List[Dict]) -> Dict[str, Any]:
        """
        创建课程分组

        Args:
            courseId: 课程ID
            groupName: 分组名称，1-20字符
            groupList: 分组成员列表，每项包含：
                studentUid: 学生UID
                isLeader: 是否组长（每组有且仅有一个组长）

        Returns:
            Dict: 响应数据，data为新建的分组ID
        """
        timeStamp, safeKey = self._get_safe_key()

        payload = {
            'SID': self.SID,
            'timeStamp': timeStamp,
            'safeKey': safeKey,
            'courseId': courseId,
            'groupName': groupName,
            'groupList': json.dumps(groupList)
        }

        return self._make_request(self.urls.addCourseGroup, data=payload)

    def edit_course_group(self, courseId: int, groupId: int, groupName: str, groupList: List[Dict]) -> Dict[str, Any]:
        """
        编辑课程分组

        Args:
            courseId: 课程ID
            groupId: 分组ID
            groupName: 分组名称，1-20字符
            groupList: 分组成员列表，每项包含：
                studentUid: 学生UID
                isLeader: 是否组长（每组有且仅有一个组长）

        Returns:
            Dict: 响应数据
        """
        timeStamp, safeKey = self._get_safe_key()

        payload = {
            'SID': self.SID,
            'timeStamp': timeStamp,
            'safeKey': safeKey,
            'courseId': courseId,
            'groupId': groupId,
            'groupName': groupName,
            'groupList': json.dumps(groupList)
        }

        return self._make_request(self.urls.editCourseGroup, data=payload)

    def del_course_group(self, courseId: int, groupId: int) -> Dict[str, Any]:
        """
        删除课程分组

        Args:
            courseId: 课程ID
            groupId: 分组ID

        Returns:
            Dict: 响应数据
        """
        timeStamp, safeKey = self._get_safe_key()

        payload = {
            'SID': self.SID,
            'timeStamp': timeStamp,
            'safeKey': safeKey,
            'courseId': courseId,
            'groupId': groupId,
        }

        return self._make_request(self.urls.delCourseGroup, data=payload)

    # =============== 课节相关接口 ===============

    def add_course_class_multiple(self, courseId: int, classJson: List[Dict]) -> Dict[str, Any]:
        """
        批量创建课节（最多50个）

        Args:
            courseId: 课程ID
            classJson: 课节信息列表，每项必填：
                className: 课节名称
                beginTime: 开始时间戳
                endTime: 结束时间戳
                teacherUid: 老师UID
              每项选填：
                folderId, teachMode, isAutoOnstage, seatNum, isHd, isDc,
                assistantUid, record, recordScene, live, replay, watchByLogin,
                allowUnloggedChat, classIntroduce, customColumn（≤50字，用于结果对应）

        Returns:
            Dict: 响应数据
        """
        timeStamp, safeKey = self._get_safe_key()

        payload = {
            'SID': self.SID,
            'timeStamp': timeStamp,
            'safeKey': safeKey,
            'courseId': courseId,
            'classJson': json.dumps(classJson)
        }

        return self._make_request(self.urls.addCourseClassMultiple, data=payload)

    def add_course_class(self, courseId: int, className: str, teacherUid: int, beginTime: int, endTime: int,
                         **kwargs) -> Dict[str, Any]:
        """
        创建课节（单个）

        Args:
            courseId: 课程ID
            className: 课节名称，1-90字符
            teacherUid: 主讲教师UID
            beginTime: 上课时间（Unix时间戳，秒，3年内）
            endTime: 下课时间（Unix时间戳，秒）
            **kwargs: 其他参数（均为选填）
                folderId: 授权云盘目录ID
                teachMode: 教学模式，1=在线教室（默认），2=智能教室
                isAutoOnstage: 学生是否自动上台，0=不自动（默认），1=自动
                seatNum: 上台学生数（不含老师），默认6，最大12
                isHd: 视频清晰度，0=标准（默认），1=高清，2=全高清
                isDc: 双摄，0=关闭（默认），3=开启全高清副摄像头
                assistantUid: 联席教师UID（与assistantUids互斥）
                assistantUids: 联席教师UID列表，如[123, 456]（与assistantUid互斥）
                record: 录课，0=关闭（默认），1=开启
                recordScene: 场景录课，0=关闭（默认），1=开启
                live: 网页直播，0=关闭（默认），1=开启
                replay: 网页回放，0=关闭（默认），1=开启
                watchByLogin: 要求登录才能观看，0=不要求（默认），1=要求
                allowUnloggedChat: 允许未登录用户聊天点赞，0=不允许，1=允许（默认）
                courseUniqueIdentity: 机构唯一标识，1-32字符
                classIntroduce: 课节简介，0-1000字符

        Returns:
            Dict: 响应数据，data=课节ID；more_data含live_url和live_info（RTMP/HLS/FLV地址）
        """
        timeStamp, safeKey = self._get_safe_key()

        base_data = {
            'SID': self.SID,
            'timeStamp': timeStamp,
            'safeKey': safeKey,
            'courseId': courseId,
            'className': className,
            'teacherUid': teacherUid,
            'beginTime': beginTime,
            'endTime': endTime
        }

        # 处理assistantUids参数
        if 'assistantUids' in kwargs and isinstance(kwargs['assistantUids'], list):
            kwargs['assistantUids'] = json.dumps(kwargs['assistantUids'])

        data = RequestUtils.prepare_request_data(base_data, **kwargs)
        return self._make_request(self.urls.addCourseClass, data=data)

    def edit_course_class(self, courseId: int, classId: int, **kwargs) -> Dict[str, Any]:
        """
        编辑课节

        Args:
            courseId: 课程ID
            classId: 课节ID
            **kwargs: 其他参数（均为选填，至少传一个）
                className: 课节名称，1-50字符
                beginTime: 上课时间（传入时endTime必填）
                endTime: 下课时间
                teacherUid: 主讲教师UID
                folderId: 授权云盘目录ID
                assistantUid: 联席教师UID（与assistantUids互斥）
                assistantUids: 联席教师UID列表，如[123, 456]
                teachMode: 教学模式，1=在线教室，2=智能教室
                isAutoOnstage: 学生是否自动上台，0=不自动，1=自动
                record: 录课，0=关闭，1=开启
                recordScene: 场景录课，0=关闭，1=开启
                live: 网页直播，0=关闭，1=开启
                replay: 网页回放，0=关闭，1=开启
                watchByLogin: 要求登录才能观看，0=不要求，1=要求
                allowUnloggedChat: 允许未登录用户聊天点赞，0=不允许，1=允许
                classIntroduce: 课节简介，0-1000字符
                omoStationBroadcast: OMO站播设置，0=关闭，1=开启

        Returns:
            Dict: 响应数据，more_data含live_url和live_info（RTMP/HLS/FLV地址）
        """
        timeStamp, safeKey = self._get_safe_key()

        base_data = {
            'SID': self.SID,
            'timeStamp': timeStamp,
            'safeKey': safeKey,
            'courseId': courseId,
            'classId': classId
        }

        if 'assistantUids' in kwargs and isinstance(kwargs['assistantUids'], list):
            kwargs['assistantUids'] = json.dumps(kwargs['assistantUids'])

        data = RequestUtils.prepare_request_data(base_data, **kwargs)
        return self._make_request(self.urls.editCourseClass, data=data)

    def del_course_class(self, courseId: int, classId: int) -> Dict[str, Any]:
        """
        删除课节

        Args:
            courseId: 课程ID
            classId: 课节ID

        Returns:
            Dict: 响应数据，errno=140课节进行中无法删除，145已结束不可删除，212已删除
        """
        timeStamp, safeKey = self._get_safe_key()

        payload = {
            'SID': self.SID,
            'timeStamp': timeStamp,
            'safeKey': safeKey,
            'courseId': courseId,
            'classId': classId,
        }

        return self._make_request(self.urls.delCourseClass, data=payload)

    def add_course_class_student(self, courseId: int, studentUid: int, classJson: List[int]) -> Dict[str, Any]:
        """
        课程下多个课节添加学生

        Args:
            courseId: 课程ID
            studentUid: 学生UID
            classJson: 课节ID列表，每次建议不超过100个

        Returns:
            Dict: 响应数据
        """
        timeStamp, safeKey = self._get_safe_key()

        payload = {
            'SID': self.SID,
            'timeStamp': timeStamp,
            'safeKey': safeKey,
            'courseId': courseId,
            'studentUid': studentUid,
            'classJson': json.dumps(classJson)
        }

        return self._make_request(self.urls.addCourseClassStudent, data=payload)

    # =============== 课程学生管理接口 ===============

    def add_course_student(self, courseId: int, studentUid: int, identity: int = 1,
                           studentName: Optional[str] = None) -> Dict[str, Any]:
        """
        课程下添加学生或旁听（单个）

        Args:
            courseId: 课程ID
            studentUid: 用户UID
            identity: 1=学生（默认），2=旁听
            studentName: 旁听者姓名，1-24字符（仅 identity=2 时有效）

        Returns:
            Dict: 响应数据，errno=163学生已在课程中，164旁听已在课程中，841加入成功但昵称同步失败
        """
        timeStamp, safeKey = self._get_safe_key()

        base_data = {
            'SID': self.SID,
            'timeStamp': timeStamp,
            'safeKey': safeKey,
            'courseId': courseId,
            'studentUid': studentUid,
            'identity': identity,
            'studentName': studentName
        }

        data = RequestUtils.prepare_request_data(base_data)
        return self._make_request(self.urls.addCourseStudent, data=data)

    def add_course_student_multiple(self, courseId: int, user_list: List[Dict], identity: int = 1) -> Dict[str, Any]:
        """
        课程下批量添加学生或旁听（旁听最多20个/次；学生建议不超过30个/次）

        Args:
            courseId: 课程ID
            user_list: 用户列表，每项包含：
                uid: 用户UID（必填）
                name: 旁听者姓名，1-24字符（选填，仅旁听有效）
                customColumn: 自定义标识（选填，用于结果对应）
            identity: 1=学生（默认），2=旁听

        Returns:
            Dict: 响应数据，data[]每项含 errno、error、customColumn
        """
        timeStamp, safeKey = self._get_safe_key()

        payload = {
            'SID': self.SID,
            'timeStamp': timeStamp,
            'safeKey': safeKey,
            'courseId': courseId,
            'identity': identity,
            'studentJson': json.dumps(user_list)
        }

        return self._make_request(self.urls.addCourseStudentMultiple, data=payload)

    def del_course_student(self, courseId: int, studentUid: int, identity: int = 1) -> Dict[str, Any]:
        """
        课程下删除学生或旁听（单个）

        Args:
            courseId: 课程ID
            studentUid: 用户UID
            identity: 1=学生（默认），2=旁听

        Returns:
            Dict: 响应数据，errno=162成员不在课程中
        """
        timeStamp, safeKey = self._get_safe_key()

        payload = {
            'SID': self.SID,
            'timeStamp': timeStamp,
            'safeKey': safeKey,
            'courseId': courseId,
            'identity': identity,
            'studentUid': studentUid
        }

        return self._make_request(self.urls.delCourseStudent, data=payload)

    def del_course_student_multiple(self, courseId: int, user_list: List[int], identity: int = 1) -> Dict[str, Any]:
        """
        课程下批量删除学生或旁听（至少1个）

        Args:
            courseId: 课程ID
            user_list: 用户UID列表
            identity: 1=学生（默认），2=旁听

        Returns:
            Dict: 响应数据，data[]每项含 errno、error
        """
        timeStamp, safeKey = self._get_safe_key()

        payload = {
            'SID': self.SID,
            'timeStamp': timeStamp,
            'safeKey': safeKey,
            'courseId': courseId,
            'identity': identity,
            'studentUidJson': json.dumps(user_list)
        }

        return self._make_request(self.urls.delCourseStudentMultiple, data=payload)

    def add_class_student_multiple(self, courseId: int, classId: int, studentJson: List[Dict],
                                   identity: int = 1) -> Dict[str, Any]:
        """
        课节下批量添加学生（建议每次不超过30个）

        Args:
            courseId: 课程ID
            classId: 课节ID
            studentJson: 学生信息列表，每项包含：
                uid: 用户UID（必填）
                customColumn: 自定义标识（选填，用于结果对应）
            identity: 1=学生（默认）

        Returns:
            Dict: 响应数据，data[]每项含 customColumn、errno、error
        """
        timeStamp, safeKey = self._get_safe_key()

        payload = {
            'SID': self.SID,
            'timeStamp': timeStamp,
            'safeKey': safeKey,
            'courseId': courseId,
            'classId': classId,
            'identity': identity,
            'studentJson': json.dumps(studentJson)
        }

        return self._make_request(self.urls.addClassStudentMultiple, data=payload)

    def del_class_student_multiple(self, courseId: int, classId: int, studentUidJson: List[int],
                                   identity: int = 1) -> Dict[str, Any]:
        """
        课节下批量删除学生（至少1个）

        Args:
            courseId: 课程ID
            classId: 课节ID
            studentUidJson: 学生UID列表
            identity: 1=学生（默认）

        Returns:
            Dict: 响应数据，data[]每项含 errno、error
        """
        timeStamp, safeKey = self._get_safe_key()

        payload = {
            'SID': self.SID,
            'timeStamp': timeStamp,
            'safeKey': safeKey,
            'courseId': courseId,
            'classId': classId,
            'identity': identity,
            'studentUidJson': json.dumps(studentUidJson)
        }

        return self._make_request(self.urls.delClassStudentMultiple, data=payload)

    def modify_class_seatNum(self, courseId: int, classId: int, seatNum: Optional[int] = None,
                             **kwargs) -> Dict[str, Any]:
        """
        修改课节上台人数及清晰度（seatNum/isHd至少传一个）

        Args:
            courseId: 课程ID
            classId: 课节ID
            seatNum: 上台学生数（不含老师），与isHd至少传一个
            **kwargs: 其他参数
                isHd: 视频清晰度，0=标准，1=高清，2=全高清（与seatNum至少传一个）
                isDc: 双摄，0=关闭，3=开启全高清副摄像头

        Returns:
            Dict: 响应数据
        """
        timeStamp, safeKey = self._get_safe_key()

        payload = {
            'SID': self.SID,
            'timeStamp': timeStamp,
            'safeKey': safeKey,
            'courseId': courseId,
            'classId': classId,
            'seatNum': seatNum
        }
        data = RequestUtils.prepare_request_data(payload, **kwargs)
        return self._make_request(self.urls.modifyClassSeatNum, data=data)

    def modify_course_teacher(self, courseId: int, teacherUid: int) -> Dict[str, Any]:
        """
        更换课程老师（将课程下所有未开始课节的老师替换为指定老师）

        Args:
            courseId: 课程ID
            teacherUid: 新教师UID

        Returns:
            Dict: 响应数据，data[]每项含 classId、errno、error
        """
        timeStamp, safeKey = self._get_safe_key()

        payload = {
            'SID': self.SID,
            'timeStamp': timeStamp,
            'safeKey': safeKey,
            'courseId': courseId,
            'teacherUid': teacherUid
        }

        return self._make_request(self.urls.modifyCourseTeacher, data=payload)

    def remove_course_teacher(self, courseId: int, teacherUid: int) -> Dict[str, Any]:
        """
        移除课程老师

        Args:
            courseId: 课程ID
            teacherUid: 老师UID

        Returns:
            Dict: 响应数据
        """
        timeStamp, safeKey = self._get_safe_key()

        payload = {
            'SID': self.SID,
            'timeStamp': timeStamp,
            'safeKey': safeKey,
            'courseId': courseId,
            'teacherUid': teacherUid
        }

        return self._make_request(self.urls.removeCourseTeacher, data=payload)

    def add_course_labels(self, courseList: List[Dict]) -> Dict[str, Any]:
        """
        批量添加/修改/删除课程标签

        Args:
            courseList: 课程标签列表，每项包含：
                courseId: 课程ID
                labelIds: 标签ID列表（传空数组则删除该课程全部标签，每课程最多10个）
                customColumn: 自定义标识（选填）

        Returns:
            Dict: 响应数据
        """
        timeStamp, safeKey = self._get_safe_key()

        payload = {
            'SID': self.SID,
            'timeStamp': timeStamp,
            'safeKey': safeKey,
            'courseList': json.dumps(courseList)
        }

        return self._make_request(self.urls.addCourseLabels, data=payload)

    def add_class_labels(self, courseId: int, classList: List[Dict]) -> Dict[str, Any]:
        """
        批量添加/修改/删除课节标签

        Args:
            courseId: 课程ID
            classList: 课节标签列表，每项包含：
                classId: 课节ID
                classLabelId: 标签ID列表（传空数组则删除该课节全部标签，每课节最多10个）
                customColumn: 自定义标识（选填）

        Returns:
            Dict: 响应数据
        """
        timeStamp, safeKey = self._get_safe_key()

        payload = {
            'SID': self.SID,
            'timeStamp': timeStamp,
            'safeKey': safeKey,
            'courseId': courseId,
            'classList': json.dumps(classList)
        }

        return self._make_request(self.urls.addClassLabels, data=payload)

    # =============== 广播/录播接口 ===============

    def set_class_video_multiple(self, courseId: int, classJson: List[Dict]) -> Dict[str, Any]:
        """
        批量设置课节录课、直播、回放

        Args:
            courseId: 课程ID
            classJson: 课节设置列表，每项包含：
                classId: 课节ID（必填）
                record: 录课，0=关闭，1=开启（可选）
                recordScene: 场景录课，0=关闭，1=开启（可选）
                live: 网页直播，0=关闭，1=开启（可选）
                replay: 网页回放，0=关闭，1=开启（可选）
                watchByLogin: 要求登录才能观看，0=不要求，1=要求（可选）
                allowUnloggedChat: 允许未登录用户聊天点赞，0=不允许，1=允许（可选）
                customColumn: 自定义标识，最多50字符（可选）

        Returns:
            Dict: 响应数据，data[]每项含 more_data（live_url、live_info）、errno、error
        """
        timeStamp, safeKey = self._get_safe_key()

        payload = {
            'SID': self.SID,
            'timeStamp': timeStamp,
            'safeKey': safeKey,
            'courseId': courseId,
            'classJson': json.dumps(classJson)
        }

        return self._make_request(self.urls.setClassVideoMultiple, data=payload)

    def delete_class_video(self, classId: int, **kwargs) -> Dict[str, Any]:
        """
        删除课节视频（删除后不可恢复）

        Args:
            classId: 课节ID
            **kwargs: 其他参数
                fileId: 视频片段ID（不传则删除该课节所有视频）

        Returns:
            Dict: 响应数据，errno=384课节未结束，633视频已锁定
        """
        timeStamp, safeKey = self._get_safe_key()

        payload = {
            'SID': self.SID,
            'timeStamp': timeStamp,
            'safeKey': safeKey,
            'classId': classId
        }
        data = RequestUtils.prepare_request_data(payload, **kwargs)
        return self._make_request(self.urls.deleteClassVideo, data=data)

    def get_webcast_url(self, courseId: int, classId: Optional[int] = None) -> Dict[str, Any]:
        """
        获取课程直播/回放播放器地址

        Args:
            courseId: 课程ID
            classId: 课节ID（可选）

        Returns:
            Dict: 响应数据，data=播放器页面URL
        """
        timeStamp, safeKey = self._get_safe_key()

        base_data = {
            'SID': self.SID,
            'timeStamp': timeStamp,
            'safeKey': safeKey,
            'courseId': courseId,
            'classId': classId
        }

        data = RequestUtils.prepare_request_data(base_data)
        return self._make_request(self.urls.getWebcastUrl, data=data)

    def update_class_lock_status(self, classId: int, isLock: int) -> Dict[str, Any]:
        """
        修改课节视频锁定状态

        Args:
            classId: 课节ID
            isLock: 1=锁定，0=解锁

        Returns:
            Dict: 响应数据
        """
        timeStamp, safeKey = self._get_safe_key()

        payload = {
            'SID': self.SID,
            'timeStamp': timeStamp,
            'safeKey': safeKey,
            'classId': classId,
            'isLock': isLock
        }

        return self._make_request(self.urls.updateClassLockStatus, data=payload)

    def get_login_linked(self, uid: int, courseId: int, classId: int, **kwargs) -> Dict[str, Any]:
        """
        获取唤醒客户端进入教室的链接

        Args:
            uid: 用户UID
            courseId: 课程ID
            classId: 课节ID
            **kwargs: 其他参数
                deviceType: 平台标识，1=PC（默认），2=iOS，3=Android
                lifeTime: 链接有效期（秒），默认86400

        Returns:
            Dict: 响应数据，data为唤醒ClassIn客户端的深链接字符串
        """
        timeStamp, safeKey = self._get_safe_key()

        base_data = {
            'SID': self.SID,
            'timeStamp': timeStamp,
            'safeKey': safeKey,
            'uid': uid,
            'courseId': courseId,
            'classId': classId
        }

        data = RequestUtils.prepare_request_data(base_data, **kwargs)
        return self._make_request(self.urls.getLoginLinked, data=data)

    # =============== LMS相关接口 ===============

    def add_course_teacher(self, courseId: int, teacherUids: List[int]) -> Dict[str, Any]:
        """
        添加课程老师（v2接口）

        Args:
            courseId: 课程ID
            teacherUids: 老师UID列表，如 [123, 456]

        Returns:
            Dict: 响应数据，data[]每项含 teacherUid、code、msg
        """
        payload = {
            'courseId': courseId,
            'teacherUids': teacherUids
        }

        headers = self._create_v2_headers(payload)
        return self._make_request(self.urls.addCourseTeacher, data=json.dumps(payload), headers=headers)

    def create_unit(self, courseId: int, unitName: str, publishFlag: int, **kwargs) -> Dict[str, Any]:
        """
        创建LMS单元（不支持创建重名单元）

        Args:
            courseId: 课程ID
            unitName: 单元名称，最多50字符
            publishFlag: 发布状态，0=草稿，2=已发布
            **kwargs: 其他参数
                content: 单元介绍

        Returns:
            Dict: 响应数据，data含 name、unitId
        """
        payload = {
            'courseId': courseId,
            'name': unitName,
            'publishFlag': publishFlag,
            **kwargs
        }

        headers = self._create_v2_headers(payload)
        return self._make_request(self.urls.createUnit, data=json.dumps(payload), headers=headers)

    def update_unit(self, courseId: int, unitId: int, **kwargs) -> Dict[str, Any]:
        """
        编辑LMS单元

        Args:
            courseId: 课程ID
            unitId: 单元ID
            **kwargs: 其他参数（至少传一个）
                name: 单元名称，最多50字符（不可与现有单元名重复）
                content: 单元介绍
                publishFlag: 发布状态，0=草稿，2=已发布（仅支持草稿→发布，不可逆）

        Returns:
            Dict: 响应数据，data含 unitId
        """
        payload = {
            'courseId': courseId,
            'unitId': unitId,
            **kwargs
        }

        headers = self._create_v2_headers(payload)
        return self._make_request(self.urls.updateUnit, data=json.dumps(payload), headers=headers)

    def delete_unit(self, courseId: int, unitId: int) -> Dict[str, Any]:
        """
        删除LMS单元（同时删除单元下所有学习活动）

        Args:
            courseId: 课程ID
            unitId: 单元ID

        Returns:
            Dict: 响应数据，data含 unitId
        """
        payload = {
            'courseId': courseId,
            'unitId': unitId,
        }

        headers = self._create_v2_headers(payload)
        return self._make_request(self.urls.deleteUnit, data=json.dumps(payload), headers=headers)

    def move_unit(self, courseId: int, unitId: int, toUnitId: int) -> Dict[str, Any]:
        """
        移动单元下的所有活动到另一个单元

        Args:
            courseId: 课程ID
            unitId: 源单元ID
            toUnitId: 目标单元ID

        Returns:
            Dict: 响应数据
        """
        payload = {
            'courseId': courseId,
            'unitId': unitId,
            'toUnitId': toUnitId,
        }

        headers = self._create_v2_headers(payload)
        return self._make_request(self.urls.moveUnit, data=json.dumps(payload), headers=headers)

    def release_activity(self, courseId: int, activityIds: List[int]) -> Dict[str, Any]:
        """
        发布活动

        Args:
            courseId: 课程ID
            activityIds: 活动ID列表

        Returns:
            Dict: 响应数据，data[]每项含 activityId、name
        """
        payload = {
            'courseId': courseId,
            'activityIds': activityIds,
        }

        headers = self._create_v2_headers(payload)
        return self._make_request(self.urls.releaseActivity, data=json.dumps(payload), headers=headers)

    def delete_activity(self, courseId: int, activityId: int) -> Dict[str, Any]:
        """
        删除活动（仅支持单个）

        Args:
            courseId: 课程ID
            activityId: 活动ID

        Returns:
            Dict: 响应数据，data含 activityId、name
        """
        payload = {
            'courseId': courseId,
            'activityId': activityId,
        }

        headers = self._create_v2_headers(payload)
        return self._make_request(self.urls.deleteActivity, data=json.dumps(payload), headers=headers)

    def add_activity_student(self, courseId: int, activityId: int, studentUids: List[int]) -> Dict[str, Any]:
        """
        添加活动成员（不适用于作业和测验类型活动）

        Args:
            courseId: 课程ID
            activityId: 活动ID
            studentUids: 学生UID列表

        Returns:
            Dict: 响应数据，data[]每项含 studentUid、code、msg
        """
        payload = {
            'courseId': courseId,
            'activityId': activityId,
            'studentUids': studentUids,
        }

        headers = self._create_v2_headers(payload)
        return self._make_request(self.urls.activity_addStudent, data=json.dumps(payload), headers=headers)

    def delete_activity_student(self, courseId: int, activityId: int, studentUids: List[int]) -> Dict[str, Any]:
        """
        删除活动成员

        Args:
            courseId: 课程ID
            activityId: 活动ID
            studentUids: 学生UID列表

        Returns:
            Dict: 响应数据
        """
        payload = {
            'courseId': courseId,
            'activityId': activityId,
            'studentUids': studentUids,
        }

        headers = self._create_v2_headers(payload)
        return self._make_request(self.urls.activity_deleteStudent, data=json.dumps(payload), headers=headers)

    def create_activity_no_class(self, courseId: int, unitId: int, activityType: int,
                                 name: str, teacherUid: int, **kwargs) -> Dict[str, Any]:
        """
        创建非课堂LMS活动

        Args:
            courseId: 课程ID
            unitId: 单元ID
            activityType: 活动类型，2=作业, 3=测验, 4=录播课, 5=学习资料, 6=讨论, 7=答题卡, 8=签到
            name: 活动名称，最多50字符
            teacherUid: 老师UID
            **kwargs: 其他参数
                startTime: 开始时间戳
                endTime: 结束时间戳

        Returns:
            Dict: 响应数据
        """
        payload = {
            'courseId': courseId,
            'unitId': unitId,
            'activityType': activityType,
            'name': name,
            'teacherUid': teacherUid,
            **kwargs
        }

        headers = self._create_v2_headers(payload)
        return self._make_request(self.urls.createActivityNoClass, data=json.dumps(payload), headers=headers)

    def create_lms_lesson(self, courseId: int, lessonName: str, teacherUid: int, startTime: int, endTime: int,
                          **kwargs) -> Dict[str, Any]:
        """
        创建LMS课堂活动（v2接口）

        Args:
            courseId: 课程ID
            lessonName: 课堂名称，最多50字符
            teacherUid: 主讲教师UID
            startTime: 开始时间（Unix时间戳，秒）
            endTime: 结束时间（Unix时间戳，秒）
            **kwargs: 其他参数（均为选填）
                unitId: 所属单元ID（不传则放入未命名单元）
                assistantUids: 联席教师UID列表，如[123, 456]
                cameraHide: 隐藏坐席区，0=不隐藏（默认），1=隐藏
                isAutoOnstage: 学生自动上台，0=不自动，1=自动（默认）
                seatNum: 上台人数（含老师），默认7
                isHd: 视频清晰度，0=标准（默认），1=高清，2=全高清
                isDc: 双摄，0=关闭（默认），3=开启
                recordType: 录课类型，0=录教室（默认），1=录现场，2=两者
                recordState: 录课，0=关闭（默认），1=开启
                liveState: 直播，0=关闭（默认），1=开启
                openState: 公开回放，0=不公开（默认），1=公开
                isAllowCheck: 允许互查报告，0=不允许，1=允许（默认）
                uniqueIdentity: 唯一标识，1-32字符
                omoStationBroadcast: OMO站播，0=关闭，1=开启

        Returns:
            Dict: 响应数据，data含 activityId、classId、name、live_url、live_info（RTMP/HLS/FLV）
        """
        payload = {
            'courseId': courseId,
            'name': lessonName,
            'teacherUid': teacherUid,
            'startTime': startTime,
            'endTime': endTime,
            **kwargs
        }

        headers = self._create_v2_headers(payload)
        return self._make_request(self.urls.createClass, data=json.dumps(payload), headers=headers)

    def update_lms_lesson(self, courseId: int, activityId: int, **kwargs) -> Dict[str, Any]:
        """
        编辑LMS课堂活动（v2接口）

        Args:
            courseId: 课程ID
            activityId: 课堂活动ID
            **kwargs: 其他参数（均为选填，至少传一个）
                unitId: 修改所属单元ID
                name: 课堂名称（对应create_lms_lesson中的lessonName）
                teacherUid: 主讲教师UID
                assistantUids: 联席教师UID列表
                startTime: 开始时间（Unix时间戳，秒）
                endTime: 结束时间（Unix时间戳，秒）
                seatNum: 上台人数（含老师）
                isHd: 视频清晰度，0=标准，1=高清，2=全高清
                isDc: 双摄，0=关闭，3=开启
                cameraHide: 隐藏坐席区，0=不隐藏，1=隐藏
                isAutoOnstage: 学生自动上台，0=不自动，1=自动
                recordType: 录课类型，0=录教室，1=录现场，2=两者
                recordState: 录课，0=关闭，1=开启
                liveState: 直播，0=关闭，1=开启
                openState: 公开回放，0=不公开，1=公开
                isAllowCheck: 允许互查报告，0=不允许，1=允许
                omoStationBroadcast: OMO站播，0=关闭，1=开启

        Returns:
            Dict: 响应数据，data含 activityId、name
        """
        payload = {
            'courseId': courseId,
            'activityId': activityId,
            **kwargs
        }

        headers = self._create_v2_headers(payload)
        return self._make_request(self.urls.updateClass, data=json.dumps(payload), headers=headers)

    # =============== 在线双师接口 ===============

    def add_newDoubleTeacher_lesson(self, mainCourseId: int, mainClassId: int,
                                    subClassJson: List[Dict]) -> Dict[str, Any]:
        """
        创建在线双师课节（单个主课节最多绑定100个子课节）

        Args:
            mainCourseId: 主课程ID
            mainClassId: 主课节ID（可以是普通课节或LMS课堂的classId）
            subClassJson: 子课节信息列表，每项包含：
                courseId: 子课节所属课程ID（必填）
                className: 子课节名称，最多50字符（必填）
                assistantUids: 联席教师UID列表（可选）
                cameraHide: 隐藏坐席区，0=不隐藏（默认），1=隐藏（可选）
                isAutoOnstage: 学生自动上台，1=不自动（默认），2=自动（可选）
                seatNum: 上台人数（含老师），默认7（可选）
                isHd: 视频清晰度，0=标准，1=高清，2=全高清（可选）
                isDc: 双摄，0=关闭，3=开启（可选）
                useCoMainRecord: 使用主课节录课，1=是，0=否（可选）
                recordState: 录课，0=关闭，1=开启（可选）
                recordType: 录课类型，0=录教室，1=录现场，2=两者（可选）
                liveState: 直播，0=关闭，1=开启（可选）
                openState: 公开回放，0=不公开，1=公开（可选）
                uniqueIdentity: 唯一标识，最多32字符（可选）

        Returns:
            Dict: 响应数据，data含 mainClassId、mainCourseId、subClassData[]（含classId/courseId/className/liveUrl/liveInfo）
        """
        payload = {
            'mainCourseId': mainCourseId,
            'mainClassId': mainClassId,
            'subClassJson': subClassJson
        }

        headers = self._create_v2_headers(payload)
        return self._make_request(self.urls.onlineDoubleTeacher_addClass, data=json.dumps(payload),
                                  headers=headers)

    def edit_newDoubleTeacher_lesson(self, courseId: int, classId: int, **kwargs) -> \
            Dict[str, Any]:
        """
        编辑在线双师课节

        Args:
            courseId: 课程ID
            classId: 课节ID（主课节或子课节）
            **kwargs: 其他参数（均为选填，至少传一个）
                className: 子课节名称，最多50字符
                teacherUid: 主讲教师UID（仅主课节支持）
                startTime: 开始时间（Unix时间戳，仅主课节支持）
                endTime: 结束时间（Unix时间戳，仅主课节支持）
                assistantUids: 联席教师UID列表
                cameraHide: 隐藏坐席区，0=不隐藏，1=隐藏
                isAutoOnstage: 学生自动上台，1=不自动，2=自动
                seatNum: 上台人数（含老师）
                isHd: 视频清晰度，0=标准，1=高清，2=全高清
                isDc: 双摄，0=关闭，3=开启
                useCoMainRecord: 使用主课节录课，1=是，0=否（仅子课节支持）
                recordType: 录课类型，0=录教室，1=录现场，2=两者
                recordState: 录课，0=关闭，1=开启
                liveState: 直播，0=关闭，1=开启
                openState: 公开回放，0=不公开，1=公开

        Returns:
            Dict: 响应数据，data[]每项含 isMainClass、classId、liveUrl、liveInfo、code、msg
        """
        payload = {
            'courseId': courseId,
            'classId': classId,
            **kwargs
        }

        headers = self._create_v2_headers(payload)
        return self._make_request(self.urls.onlineDoubleTeacher_editClass, data=json.dumps(payload),
                                  headers=headers)

    def del_newDoubleTeacher_lesson(self, courseId: int, classId: int) -> Dict[str, Any]:
        """
        删除在线双师课节（删除主课节时子课节同步删除；删除子课节不影响主课节）

        Args:
            courseId: 课程ID
            classId: 课节ID（主课节或子课节）

        Returns:
            Dict: 响应数据，data[]每项含 classId、code、msg
        """
        payload = {
            'courseId': courseId,
            'classId': classId
        }

        headers = self._create_v2_headers(payload)
        return self._make_request(self.urls.onlineDoubleTeacher_deleteClass, data=json.dumps(payload),
                                  headers=headers)

    # =============== 机构相关接口 ===============

    def add_school_label(self, labelName: str) -> Dict[str, Any]:
        """
        添加机构标签（机构最多100个标签，颜色随机分配）

        Args:
            labelName: 标签名称，1-20字符

        Returns:
            Dict: 响应数据，data.labelId=新建标签ID；errno=353标签名已存在（返回已有ID），354超出数量限制
        """
        timeStamp, safeKey = self._get_safe_key()

        payload = {
            'SID': self.SID,
            'timeStamp': timeStamp,
            'safeKey': safeKey,
            'labelName': labelName
        }

        return self._make_request(self.urls.addSchoolLabel, data=payload)

    def update_school_label(self, labelId: int, labelName: str) -> Dict[str, Any]:
        """
        修改机构标签

        Args:
            labelId: 标签ID
            labelName: 标签名称，1-20字

        Returns:
            Dict: 响应数据
        """
        timeStamp, safeKey = self._get_safe_key()

        payload = {
            'SID': self.SID,
            'timeStamp': timeStamp,
            'safeKey': safeKey,
            'labelId': labelId,
            'labelName': labelName
        }

        return self._make_request(self.urls.updateSchoolLabel, data=payload)

    def delete_school_label(self, labelId: int) -> Dict[str, Any]:
        """
        删除机构标签

        Args:
            labelId: 标签ID

        Returns:
            Dict: 响应数据
        """
        timeStamp, safeKey = self._get_safe_key()

        payload = {
            'SID': self.SID,
            'timeStamp': timeStamp,
            'safeKey': safeKey,
            'labelId': labelId
        }

        return self._make_request(self.urls.deleteSchoolLabel, data=payload)

    def modify_school_conf(self, **kwargs) -> Dict[str, Any]:
        """
        修改学校设置

        Args:
            **kwargs: 至少传一个参数：
                allowViewReplay: 正式学生和老师是否可课后看回放，0=不允许，1=允许
                allowNewStudentViewReplay: 新生是否可查看历史课节回放，0=不允许，1=允许

        Returns:
            Dict: 响应数据
        """
        payload = {**kwargs}
        headers = self._create_v2_headers(payload)
        return self._make_request(self.urls.modifySchoolConf, data=json.dumps(payload), headers=headers)

    # =============== 班级群相关接口 ===============

    def modify_group_member_nickname(self, courseId: int) -> Dict[str, Any]:
        """
        修改群成员的班级昵称（将课程群中所有学生/旁听的显示名称替换为机构学生姓名）

        Args:
            courseId: 课程ID

        Returns:
            Dict: 响应数据
        """
        timeStamp, safeKey = self._get_safe_key()

        base_data = {
            'SID': self.SID,
            'timeStamp': timeStamp,
            'safeKey': safeKey,
            'courseId': courseId
        }

        return self._make_request(self.urls.modifyGroupMemberNickname, data=base_data)

    # =============== 云盘相关接口 ===============

    def get_folder_list(self) -> Dict[str, Any]:
        """
        获取机构云盘两级文件夹列表

        Returns:
            Dict: 响应数据，data以一级文件夹ID为键，值为二级文件夹数组（每项含id/pid/name）
        """
        timeStamp, safeKey = self._get_safe_key()

        payload = {
            'SID': self.SID,
            'timeStamp': timeStamp,
            'safeKey': safeKey
        }

        return self._make_request(self.urls.getFolderList, data=payload)

    def get_cloud_list(self, **kwargs) -> Dict[str, Any]:
        """
        获取指定文件夹下的文件及文件夹列表

        Args:
            **kwargs: 其他参数
                folderId: 目标文件夹ID（不传则返回顶层内容）

        Returns:
            Dict: 响应数据，folder_list[]（folder_id/folder_name/is_system_folder）、file_list[]（id/file_name/file_size）
        """
        timeStamp, safeKey = self._get_safe_key()

        base_data = {
            'SID': self.SID,
            'timeStamp': timeStamp,
            'safeKey': safeKey
        }

        data = RequestUtils.prepare_request_data(base_data, **kwargs)
        return self._make_request(self.urls.getCloudList, data=data)

    def get_top_folder_id(self) -> Dict[str, Any]:
        """
        获取机构云盘顶级文件夹ID

        Returns:
            Dict: 响应数据，data=顶级文件夹ID字符串
        """
        timeStamp, safeKey = self._get_safe_key()

        payload = {
            'SID': self.SID,
            'timeStamp': timeStamp,
            'safeKey': safeKey
        }

        return self._make_request(self.urls.getTopFolderId, data=payload)

    def upload_file(self, folderId: int, file_path: str) -> Dict[str, Any]:
        """
        上传文件到云盘（最大500MB，文件名1-128字符）

        Args:
            folderId: 目标文件夹ID
            file_path: 本地文件路径

        Returns:
            Dict: 响应数据，data=文件ID；errno=211文件超出大小限制，31000存储空间不足
        """
        timeStamp, safeKey = self._get_safe_key()

        data = {'SID': self.SID, 'timeStamp': timeStamp, 'safeKey': safeKey, 'folderId': folderId}
        return self._make_file_request(self.urls.uploadFile, data, file_path)

    def rename_file(self, fileId: int, fileName: str) -> Dict[str, Any]:
        """
        重命名云盘文件

        Args:
            fileId: 文件ID
            fileName: 新文件名，1-128字符

        Returns:
            Dict: 响应数据，errno=198文件不存在，199不属于本机构，200同名文件已存在
        """
        timeStamp, safeKey = self._get_safe_key()

        payload = {
            'SID': self.SID,
            'timeStamp': timeStamp,
            'safeKey': safeKey,
            'fileId': fileId,
            'fileName': fileName
        }

        return self._make_request(self.urls.renameFile, data=payload)

    def del_file(self, fileId: int) -> Dict[str, Any]:
        """
        删除云盘文件

        Args:
            fileId: 文件ID

        Returns:
            Dict: 响应数据
        """
        timeStamp, safeKey = self._get_safe_key()

        payload = {
            'SID': self.SID,
            'timeStamp': timeStamp,
            'safeKey': safeKey,
            'fileId': fileId
        }

        return self._make_request(self.urls.delFile, data=payload)

    def create_folder(self, folderId: int, folderName: str) -> Dict[str, Any]:
        """
        创建云盘文件夹（最多15级深度，机构最多5000个文件夹）

        Args:
            folderId: 父文件夹ID
            folderName: 文件夹名称，1-128字符

        Returns:
            Dict: 响应数据，data=新文件夹ID；errno=206同名已存在，207超出层级限制，208超出数量限制
        """
        timeStamp, safeKey = self._get_safe_key()

        payload = {
            'SID': self.SID,
            'timeStamp': timeStamp,
            'safeKey': safeKey,
            'folderId': folderId,
            'folderName': folderName
        }

        return self._make_request(self.urls.createFolder, data=payload)

    def rename_folder(self, folderId: int, folderName: str) -> Dict[str, Any]:
        """
        重命名云盘文件夹

        Args:
            folderId: 文件夹ID
            folderName: 新文件夹名称，1-128字符

        Returns:
            Dict: 响应数据
        """
        timeStamp, safeKey = self._get_safe_key()

        payload = {
            'SID': self.SID,
            'timeStamp': timeStamp,
            'safeKey': safeKey,
            'folderId': folderId,
            'folderName': folderName
        }

        return self._make_request(self.urls.renameFolder, data=payload)

    def del_folder(self, folderId: int) -> Dict[str, Any]:
        """
        删除云盘文件夹（递归删除子文件夹及所有文件，不可恢复）

        Args:
            folderId: 文件夹ID

        Returns:
            Dict: 响应数据
        """
        timeStamp, safeKey = self._get_safe_key()

        payload = {
            'SID': self.SID,
            'timeStamp': timeStamp,
            'safeKey': safeKey,
            'folderId': folderId
        }

        return self._make_request(self.urls.delFolder, data=payload)

    # =============== 其他方法 ===============

    def close(self):
        """关闭会话"""
        if self.session:
            self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
