<div align="center">

# eeo

ClassIn 在线教育平台 Python SDK，一行代码调用全量 API

[![PyPI](https://img.shields.io/pypi/v/eeo?logo=pypi&logoColor=white&color=3776AB)](https://pypi.org/project/eeo/)
[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](./LICENSE)

> 🇺🇸 [English version →](README-EN.md)

</div>

---

## 简介

`eeo` 是 ClassIn 在线教育平台的API Python SDK，封装了用户管理、课程管理、课节管理、LMS 学习系统、在线双师、云盘等全量 REST API。无需手动处理签名计算、参数过滤和响应解析。

## 特性

- **双签名模式** — 自动处理 v1（MD5 表单签名）和 v2（JSON + Header 签名），无需手动计算
- **文件上传** — `register`、`add_teacher`、`add_course`、`upload_file` 等接口原生支持本地文件
- **参数过滤** — 自动剔除值为 `None` 的参数，无需手动组装字典
- **连接复用** — 基于 `requests.Session`，支持 `with` 上下文管理器
- **开箱即用** — 唯一依赖 `requests`，无需额外配置

## 安装

```bash
pip install eeo
```

**前置要求：** Python >= 3.9.2

## 快速开始

```python
import eeo

api = eeo.ClassInAPI(
    school_uid=123456,
    school_secret="your_school_secret",
)

# 注册用户
result = api.register("13800138000", "password123", nickname="张三")
print(result)  # {"code": 0, "data": 100001, ...}

# 创建课程
course = api.add_course("高中数学", mainTeacherUid=100001)

# 创建课节
import time
api.add_course_class(
    courseId=course["data"],
    className="第一讲：集合",
    teacherUid=100001,
    beginTime=int(time.time()) + 3600,
    endTime=int(time.time()) + 7200,
)
```

推荐使用上下文管理器，退出时自动关闭连接：

```python
with eeo.ClassInAPI(school_uid=123456, school_secret="your_secret") as api:
    api.add_course("物理课")
```

## 初始化参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `school_uid` | `int` | ✅ | 学校账号 UID |
| `school_secret` | `str` | ✅ | API 密钥 |
| `domain` | `str` | ❌ | API 域名，默认 `https://api.eeo.cn` |

> [!NOTE]
> `school_uid` 和 `school_secret` 可在 ClassIn 管理后台的「开发者设置」中获取。

## 接口速查

### 用户管理

```python
# 注册（手机号或邮箱自动识别；file_path 可附带头像）
api.register(account, password, nickname=None, addToSchoolMember=None, file_path=None)
api.register_multiple(userJson)               # 批量注册，最多10个，List[Dict]
api.modify_password(uid, oldMd5pass, password=None, md5pass=None)

# 老师
api.add_teacher(teacherAccount, teacherName, file_path=None)
api.edit_teacher(teacherUid, teacherName, file_path=None)
api.stop_using_teacher(teacherUid)
api.restart_using_teacher(teacherUid)

# 学生
api.add_school_student(studentAccount, studentName)
api.edit_school_student(studentUid, studentName)
api.modify_course_student_nickname(studentUids)         # 同步班级昵称，v2，List[int]
api.update_class_student_comment(classId, commentJson)  # 更新课节学生评价，List[Dict]
```

### 课程管理

```python
api.add_course(courseName, file_path=None, **kwargs)    # file_path 可附带封面
api.edit_course(courseId, file_path=None, **kwargs)
api.end_course(courseId)

# 老师
api.add_course_teacher(courseId, teacherUids)           # v2，支持批量
api.modify_course_teacher(courseId, teacherUid)
api.remove_course_teacher(courseId, teacherUid)

# 分组
api.add_course_group(courseId, groupName, groupList)
api.edit_course_group(courseId, groupId, groupName, groupList)
api.del_course_group(courseId, groupId)

# 标签
api.add_course_labels(courseList)
```

### 课节管理

```python
# 创建
api.add_course_class(courseId, className, teacherUid, beginTime, endTime, **kwargs)
api.add_course_class_multiple(courseId, classJson)      # 批量，最多50个

# 编辑 / 删除
api.edit_course_class(courseId, classId, **kwargs)
api.del_course_class(courseId, classId)

# 学生增删
api.add_course_student(courseId, studentUid, identity=1, studentName=None)
api.del_course_student(courseId, studentUid, identity=1)
api.add_course_student_multiple(courseId, user_list, identity=1)
api.del_course_student_multiple(courseId, user_list, identity=1)
api.add_class_student_multiple(courseId, classId, studentJson, identity=1)
api.del_class_student_multiple(courseId, classId, studentUidJson, identity=1)
api.add_course_class_student(courseId, studentUid, classJson)  # 指定课节报名，List[int]

# 直播 / 录播
api.set_class_video_multiple(courseId, classJson)
api.get_webcast_url(courseId, classId=None)
api.update_class_lock_status(classId, isLock)
api.delete_class_video(classId, **kwargs)
api.get_login_linked(uid, courseId, classId, **kwargs)

# 其他
api.modify_class_seatNum(courseId, classId, seatNum=None, **kwargs)
api.modify_group_member_nickname(courseId)
```

### 标签管理

```python
api.add_school_label(labelName)
api.update_school_label(labelId, labelName)
api.delete_school_label(labelId)
api.add_class_labels(courseId, classList)               # List[Dict]
```

### LMS 学习系统（v2 签名）

```python
# 单元
api.create_unit(courseId, unitName, publishFlag, **kwargs)  # publishFlag: 0=草稿, 2=发布
api.update_unit(courseId, unitId, **kwargs)
api.delete_unit(courseId, unitId)
api.move_unit(courseId, unitId, toUnitId)

# 活动
api.create_lms_lesson(courseId, lessonName, teacherUid, startTime, endTime, **kwargs)
api.update_lms_lesson(courseId, activityId, **kwargs)
api.create_activity_no_class(courseId, unitId, activityType, name, teacherUid, **kwargs)
api.release_activity(courseId, activityIds)             # List[int]
api.delete_activity(courseId, activityId)
api.add_activity_student(courseId, activityId, studentUids)
api.delete_activity_student(courseId, activityId, studentUids)
```

### 在线双师

```python
api.add_newDoubleTeacher_lesson(mainCourseId, mainClassId, subClassJson)
api.edit_newDoubleTeacher_lesson(courseId, classId, **kwargs)
api.del_newDoubleTeacher_lesson(courseId, classId)
```

### 云盘管理

```python
# 文件夹
api.get_folder_list()
api.get_cloud_list(**kwargs)
api.get_top_folder_id()
api.create_folder(folderId, folderName)
api.rename_folder(folderId, folderName)
api.del_folder(folderId)

# 文件（最大 500MB）
api.upload_file(folderId, file_path)
api.rename_file(fileId, fileName)
api.del_file(fileId)
```

### 机构设置

```python
api.modify_school_conf(**kwargs)
# 可选参数：allowViewReplay、allowNewStudentViewReplay
```

## 项目结构

```
eeo/
├── __init__.py     # 公开导出：ClassInAPI, ApiUrls, RequestUtils, SignatureUtils
├── api.py          # ClassInAPI 主客户端，所有接口方法（70+）
├── urls.py         # ApiUrls，集中管理所有 API 端点 URL
└── utils.py        # SignatureUtils（v1/v2 签名）、RequestUtils（参数处理、响应解析）
```

## 许可证

[MIT License](./LICENSE) · 如有疑问请联系 eeoapisupport@eeoa.com · [官方文档](https://docs.eeo.cn/api/)
