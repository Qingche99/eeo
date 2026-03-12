# -*- coding: utf-8 -*-
"""
@Author   : 清澈
@Time     :2026/1/15
@File     :urls.py
@IDE      :PyCharm
"""


class ApiUrls:
    """ClassIn API URL配置类"""

    def __init__(self, domain='https://api.eeo.cn'):
        """
        初始化URL配置

        Args:
            domain: API域名，默认为 https://api.eeo.cn
        """
        self.base_domain = domain
        self.partner_api = f'{domain}/partner/api/course.api.php'
        self.cloud_api = f'{domain}/partner/api/cloud.api.php'
        self.lms_api = f'{domain}/lms'

        # 初始化所有URL
        self._init_urls()

    def _init_urls(self):
        """初始化所有API URL"""
        self._init_user_urls()
        self._init_course_urls()
        self._init_class_urls()
        self._init_cloud_urls()
        self._init_lms_urls()
        self._init_school_urls()

    def _init_user_urls(self):
        """用户相关接口"""
        self.register = f'{self.partner_api}?action=register'
        self.registerMultiple = f'{self.partner_api}?action=registerMultiple'
        self.modifyPassword = f'{self.partner_api}?action=modifyPassword'
        self.addSchoolStudent = f'{self.partner_api}?action=addSchoolStudent'
        self.editSchoolStudent = f'{self.partner_api}?action=editSchoolStudent'
        self.addTeacher = f'{self.partner_api}?action=addTeacher'
        self.editTeacher = f'{self.partner_api}?action=editTeacher'
        self.stopUsingTeacher = f'{self.partner_api}?action=stopUsingTeacher'
        self.restartUsingTeacher = f'{self.partner_api}?action=restartUsingTeacher'
        self.modifyCourseStudentNickName = f'{self.base_domain}/schooluser/modifyCourseStudentNickName'
        self.updateClassStudentComment = f'{self.partner_api}?action=updateClassStudentComment'

    def _init_course_urls(self):
        """课程相关接口"""
        self.addCourse = f'{self.partner_api}?action=addCourse'
        self.editCourse = f'{self.partner_api}?action=editCourse'
        self.endCourse = f'{self.partner_api}?action=endCourse'
        self.modifyCourseTeacher = f'{self.partner_api}?action=modifyCourseTeacher'
        self.removeCourseTeacher = f'{self.partner_api}?action=removeCourseTeacher'

        # 添加课程老师（v2接口，路径特殊）
        self.addCourseTeacher = f'{self.base_domain}/course/addCourseTeacher'

        # 课程分组
        self.addCourseGroup = f'{self.partner_api}?action=addCourseGroup'
        self.editCourseGroup = f'{self.partner_api}?action=editCourseGroup'
        self.delCourseGroup = f'{self.partner_api}?action=delCourseGroup'

    def _init_class_urls(self):
        """课节相关接口"""
        self.addCourseClass = f'{self.partner_api}?action=addCourseClass'
        self.addCourseClassMultiple = f'{self.partner_api}?action=addCourseClassMultiple'
        self.editCourseClass = f'{self.partner_api}?action=editCourseClass'
        self.delCourseClass = f'{self.partner_api}?action=delCourseClass'
        self.modifyClassSeatNum = f'{self.partner_api}?action=modifyClassSeatNum'

        # 操作课程或课节学生
        self.addCourseStudent = f'{self.partner_api}?action=addCourseStudent'
        self.delCourseStudent = f'{self.partner_api}?action=delCourseStudent'
        self.addCourseStudentMultiple = f'{self.partner_api}?action=addCourseStudentMultiple'
        self.delCourseStudentMultiple = f'{self.partner_api}?action=delCourseStudentMultiple'
        self.addClassStudentMultiple = f'{self.partner_api}?action=addClassStudentMultiple'
        self.delClassStudentMultiple = f'{self.partner_api}?action=delClassStudentMultiple'
        self.addCourseClassStudent = f'{self.partner_api}?action=addCourseClassStudent'

        # 直播相关
        self.setClassVideoMultiple = f'{self.partner_api}?action=setClassVideoMultiple'
        self.deleteClassVideo = f'{self.partner_api}?action=deleteClassVideo'
        self.updateClassLockStatus = f'{self.partner_api}?action=updateClassLockStatus'
        self.getWebcastUrl = f'{self.partner_api}?action=getWebcastUrl'

        # 其他
        self.getLoginLinked = f'{self.partner_api}?action=getLoginLinked'
        self.modifyGroupMemberNickname = f'{self.partner_api}?action=modifyGroupMemberNickname'

        # 标签相关
        self.addSchoolLabel = f'{self.partner_api}?action=addSchoolLabel'
        self.updateSchoolLabel = f'{self.partner_api}?action=updateSchoolLabel'
        self.deleteSchoolLabel = f'{self.partner_api}?action=deleteSchoolLabel'
        self.addCourseLabels = f'{self.partner_api}?action=addCourseLabels'
        self.addClassLabels = f'{self.partner_api}?action=addClassLabels'

    def _init_cloud_urls(self):
        """云盘相关接口"""
        self.getFolderList = f'{self.cloud_api}?action=getFolderList'
        self.getCloudList = f'{self.cloud_api}?action=getCloudList'
        self.getTopFolderId = f'{self.cloud_api}?action=getTopFolderId'
        self.uploadFile = f'{self.cloud_api}?action=uploadFile'
        self.renameFile = f'{self.cloud_api}?action=renameFile'
        self.delFile = f'{self.cloud_api}?action=delFile'
        self.createFolder = f'{self.cloud_api}?action=createFolder'
        self.renameFolder = f'{self.cloud_api}?action=renameFolder'
        self.delFolder = f'{self.cloud_api}?action=delFolder'

    def _init_lms_urls(self):
        """LMS相关接口"""
        # 单元管理
        self.createUnit = f'{self.lms_api}/unit/create'
        self.updateUnit = f'{self.lms_api}/unit/update'
        self.deleteUnit = f'{self.lms_api}/unit/delete'
        self.moveUnit = f'{self.lms_api}/unit/move'

        # 活动管理
        self.createActivityNoClass = f'{self.lms_api}/activity/createActivityNoClass'
        self.createClass = f'{self.lms_api}/activity/createClass'
        self.updateClass = f'{self.lms_api}/activity/updateClass'
        self.releaseActivity = f'{self.lms_api}/activity/release'
        self.deleteActivity = f'{self.lms_api}/activity/delete'
        self.activity_addStudent = f'{self.lms_api}/activity/addStudent'
        self.activity_deleteStudent = f'{self.lms_api}/activity/deleteStudent'

        # 在线双师
        self.onlineDoubleTeacher_addClass = f'{self.lms_api}/onlineDoubleTeacher/addClass'
        self.onlineDoubleTeacher_editClass = f'{self.lms_api}/onlineDoubleTeacher/editClass'
        self.onlineDoubleTeacher_deleteClass = f'{self.lms_api}/onlineDoubleTeacher/deleteClass'

    def _init_school_urls(self):
        """机构相关接口"""
        self.modifySchoolConf = f'{self.base_domain}/school/modifySchoolConf'

    def set_domain(self, domain: str):
        """
        动态设置域名

        Args:
            domain: 新的API域名
        """
        self.__init__(domain)

    def get_all_urls(self) -> dict:
        """
        获取所有URL的字典表示

        Returns:
            dict: 所有URL的字典
        """
        urls = {}
        for attr_name in dir(self):
            if not attr_name.startswith('_') and not callable(getattr(self, attr_name)):
                if attr_name not in ['base_domain', 'partner_api', 'cloud_api', 'lms_api']:
                    urls[attr_name] = getattr(self, attr_name)
        return urls
