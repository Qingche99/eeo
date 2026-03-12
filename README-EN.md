<div align="center">

# eeo

Python SDK for ClassIn (EEO) online education platform — one import, full API coverage

[![PyPI](https://img.shields.io/pypi/v/eeo?logo=pypi&logoColor=white&color=3776AB)](https://pypi.org/project/eeo/)
[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](./LICENSE)

> 🇨🇳 [中文版 →](README.md)

</div>

---

## Introduction

`eeo` is the Python SDK for the ClassIn (EEO) online education platform, wrapping the full REST API: user management, course management, class scheduling, LMS, double-teacher mode, and cloud storage. No manual signature calculation, parameter filtering, or response parsing required.

## Features

- **Dual signature modes** — Automatically handles v1 (MD5 form signing) and v2 (JSON + Header signing)
- **File uploads** — Native support in `register`, `add_teacher`, `add_course`, `upload_file`, and more
- **Auto param filtering** — `None` values stripped automatically before every request
- **Connection reuse** — Built on `requests.Session` with context manager support
- **Zero config** — Single dependency on `requests`, no extra setup

## Installation

```bash
pip install eeo
```

**Prerequisites:** Python >= 3.9.2

## Quick Start

```python
import eeo

api = eeo.ClassInAPI(
    school_uid=123456,
    school_secret="your_school_secret",
)

# Register a user
result = api.register("13800138000", "password123", nickname="John")
print(result)  # {"code": 0, "data": 100001, ...}

# Create a course
course = api.add_course("High School Math", mainTeacherUid=100001)

# Create a class session
import time
api.add_course_class(
    courseId=course["data"],
    className="Lesson 1: Sets",
    teacherUid=100001,
    beginTime=int(time.time()) + 3600,
    endTime=int(time.time()) + 7200,
)
```

Use as a context manager to close the connection automatically on exit:

```python
with eeo.ClassInAPI(school_uid=123456, school_secret="your_secret") as api:
    api.add_course("Physics")
```

## Constructor Parameters

| Parameter | Type | Required | Description                                                                                                                          |
|---|---|---|--------------------------------------------------------------------------------------------------------------------------------------|
| `school_uid` | `int` | ✅ | School account UID                                                                                                                   |
| `school_secret` | `str` | ✅ | API secret key                                                                                                                       |
| `domain` | `str` | ❌ | API domain, defaults to `https://api.eeo.cn`. If the default domain fails, you can switch to the backup domain `https://api2.eeo.cn` |

> [!NOTE]
> You can obtain school_uid and school_secret in the ClassIn admin panel under "Profile ➡️ API ➡️ API Integration Key".

## API Reference

### User Management

```python
# Register (phone or email auto-detected; file_path for avatar)
api.register(account, password, nickname=None, addToSchoolMember=None, file_path=None)
api.register_multiple(userJson)               # Batch register, up to 10, List[Dict]
api.modify_password(uid, oldMd5pass, password=None, md5pass=None)

# Teachers
api.add_teacher(teacherAccount, teacherName, file_path=None)
api.edit_teacher(teacherUid, teacherName, file_path=None)
api.stop_using_teacher(teacherUid)
api.restart_using_teacher(teacherUid)

# Students
api.add_school_student(studentAccount, studentName)
api.edit_school_student(studentUid, studentName)
api.modify_course_student_nickname(studentUids)         # Sync class nicknames, v2, List[int]
api.update_class_student_comment(classId, commentJson)  # Update session comments, List[Dict]
```

### Course Management

```python
api.add_course(courseName, file_path=None, **kwargs)    # file_path for cover image
api.edit_course(courseId, file_path=None, **kwargs)
api.end_course(courseId)

# Teachers
api.add_course_teacher(courseId, teacherUids)           # v2, batch supported
api.modify_course_teacher(courseId, teacherUid)
api.remove_course_teacher(courseId, teacherUid)

# Groups
api.add_course_group(courseId, groupName, groupList)
api.edit_course_group(courseId, groupId, groupName, groupList)
api.del_course_group(courseId, groupId)

# Labels
api.add_course_labels(courseList)
```

### Class Session Management

```python
# Create
api.add_course_class(courseId, className, teacherUid, beginTime, endTime, **kwargs)
api.add_course_class_multiple(courseId, classJson)      # Batch, up to 50

# Edit & delete
api.edit_course_class(courseId, classId, **kwargs)
api.del_course_class(courseId, classId)

# Student enrollment
api.add_course_student(courseId, studentUid, identity=1, studentName=None)
api.del_course_student(courseId, studentUid, identity=1)
api.add_course_student_multiple(courseId, user_list, identity=1)
api.del_course_student_multiple(courseId, user_list, identity=1)
api.add_class_student_multiple(courseId, classId, studentJson, identity=1)
api.del_class_student_multiple(courseId, classId, studentUidJson, identity=1)
api.add_course_class_student(courseId, studentUid, classJson)  # Enroll in specific sessions, List[int]

# Live & recording
api.set_class_video_multiple(courseId, classJson)
api.get_webcast_url(courseId, classId=None)
api.update_class_lock_status(classId, isLock)
api.delete_class_video(classId, **kwargs)
api.get_login_linked(uid, courseId, classId, **kwargs)

# Other
api.modify_class_seatNum(courseId, classId, seatNum=None, **kwargs)
api.modify_group_member_nickname(courseId)
```

### Label Management

```python
api.add_school_label(labelName)
api.update_school_label(labelId, labelName)
api.delete_school_label(labelId)
api.add_class_labels(courseId, classList)               # List[Dict]
```

### LMS — Learning Management System (v2 signing)

```python
# Units
api.create_unit(courseId, unitName, publishFlag, **kwargs)  # publishFlag: 0=draft, 2=publish
api.update_unit(courseId, unitId, **kwargs)
api.delete_unit(courseId, unitId)
api.move_unit(courseId, unitId, toUnitId)

# Activities
api.create_lms_lesson(courseId, lessonName, teacherUid, startTime, endTime, **kwargs)
api.update_lms_lesson(courseId, activityId, **kwargs)
api.create_activity_no_class(courseId, unitId, activityType, name, teacherUid, **kwargs)
api.release_activity(courseId, activityIds)             # List[int]
api.delete_activity(courseId, activityId)
api.add_activity_student(courseId, activityId, studentUids)
api.delete_activity_student(courseId, activityId, studentUids)
```

### Double Teacher Mode

```python
api.add_newDoubleTeacher_lesson(mainCourseId, mainClassId, subClassJson)
api.edit_newDoubleTeacher_lesson(courseId, classId, **kwargs)
api.del_newDoubleTeacher_lesson(courseId, classId)
```

### Cloud Storage

```python
# Folders
api.get_folder_list()
api.get_cloud_list(**kwargs)
api.get_top_folder_id()
api.create_folder(folderId, folderName)
api.rename_folder(folderId, folderName)
api.del_folder(folderId)

# Files (max 500MB)
api.upload_file(folderId, file_path)
api.rename_file(fileId, fileName)
api.del_file(fileId)
```

### School Configuration

```python
api.modify_school_conf(**kwargs)
# Options: allowViewReplay, allowNewStudentViewReplay
```

## Project Structure

```
eeo/
├── __init__.py     # Public exports: ClassInAPI, ApiUrls, RequestUtils, SignatureUtils
├── api.py          # ClassInAPI main client with all API methods (70+)
├── urls.py         # ApiUrls, centralized API endpoint management
└── utils.py        # SignatureUtils (v1/v2 signing), RequestUtils (params & response)
```

## License

[MIT License](./LICENSE) · For support, contact eeoapisupport@eeoa.com · [API Docs](https://docs.eeo.cn/api/)
