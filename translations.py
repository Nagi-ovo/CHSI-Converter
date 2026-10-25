"""Only explicit translations; unknown official names require user input."""

LABELS = {
    "姓名": ("Name", "Name"),
    "性别": ("Gender", "Gender"),
    "出生日期": ("Date of birth", "Date of Birth"),
    "民族": ("Ethnicity", "Ethnic"),
    "学校名称": ("Institution", "Institution"),
    "院校": ("Institution", "Institution"),
    "层次": ("Level", "Levels"),
    "专业": ("Major", "Major"),
    "学制": ("Length of study", "Educational System"),
    "学历类别": ("Education type", "Type"),
    "学习形式": ("Mode of study", "Form"),
    "分院": ("Branch", "Branch"),
    "系所": ("Department", "Faculties"),
    "院系": ("Department", "Faculties"),
    "入学日期": ("Enrollment date", "Date of Enrollment"),
    "学籍状态": ("Student status", "School Status"),
    "离校日期": ("Leaving date", "Date of Leaving Institution"),
    "毕业日期": ("Graduation date", "Date of Leaving Institution"),
    "预计毕业日期": ("Expected graduation", "Expected Graduation Date"),
    "证件号码": ("ID number", "Id Number"),
    "班级": ("Class", "Class"),
    "学号": ("Student number", "Student Number"),
}

FOOTNOTES = {
    "注意事项：": "Notes:",
    "1、《学籍在线验证报告》是教育部学籍电子注册备案的查询结果。": (
        "1. This report presents the query result of student records electronically "
        "registered with the Ministry of Education."
    ),
    "2、报告内容如有修改，请以最新在线验证的内容为准。": (
        "2. If the report is updated, refer to the latest information "
        "available through online verification."
    ),
    "3、未经学籍信息权属人同意，不得将报告用于违背权属人意愿之用途。": (
        "3. Without the record holder's consent, this report must not be used "
        "for purposes contrary to their wishes."
    ),
    (
        "4、报告在线验证有效期由报告权属人设置（1~6个月），其在报告验证到期前可再次延长验证有效期。"
    ): (
        "4. The holder sets the validity period (1-6 months) and may extend it "
        "before the current verification period expires."
    ),
}
