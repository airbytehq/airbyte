<#if addHeader == true>
accountEmail,accountID,actionList,approved,approvers,created,currency,entryID,isACHReimbursed,managerEmail,managerUserID,managerPayrollID,managerFirstName,managerLastName,managerFullName,policyName,policyID,reimbursed,reportID,oldReportID,reportName,status,displayStatus,submitted,employeeCustomField1,employeeCustomField2,submitterFirstName,submitterLastName,submitterFullName,total
</#if>
<#list reports as report>
<#-- Extract action types into a CSV string -->
<#assign actionTypes = "">
<#if report.actionList??>
  <#assign actionTypesList = []>
  <#list report.actionList as act>
    <#if act.action??><#assign actionTypesList = actionTypesList + [act.action]></#if>
  </#list>
  <#assign actionTypes = actionTypesList?join(", ")>
</#if>
<#-- Extract approver emails into a CSV string -->
<#assign approverEmails = "">
<#if report.approvers??>
  <#assign approverEmailsList = []>
  <#list report.approvers as app>
    <#if app.email??><#assign approverEmailsList = approverEmailsList + [app.email]></#if>
  </#list>
  <#assign approverEmails = approverEmailsList?join(", ")>
</#if>
<#-- Safely handle boolean and numeric conversions -->
<#assign isACH = "">
<#if report.isACHReimbursed??>
  <#assign isACH = report.isACHReimbursed?string("true", "false")>
</#if>
<#assign totalAmount = "">
<#if report.total??>
  <#assign totalAmount = report.total?c>
</#if>
<#-- Output all fields row by row -->
"${(report.accountEmail!"")?replace('"', '""')}",<#t>
"${(report.accountID!"")?replace('"', '""')}",<#t>
"${actionTypes?replace('"', '""')}",<#t>
"${(report.approved!"")?replace('"', '""')}",<#t>
"${approverEmails?replace('"', '""')}",<#t>
"${(report.created!"")?replace('"', '""')}",<#t>
"${(report.currency!"")?replace('"', '""')}",<#t>
"${(report.entryID!"")?replace('"', '""')}",<#t>
"${isACH}",<#t>
"${(report.managerEmail!"")?replace('"', '""')}",<#t>
"${(report.managerUserID!"")?replace('"', '""')}",<#t>
"${(report.managerPayrollID!"")?replace('"', '""')}",<#t>
"${((report.manager.firstName)!"")?replace('"', '""')}",<#t>
"${((report.manager.lastName)!"")?replace('"', '""')}",<#t>
"${((report.manager.fullName)!"")?replace('"', '""')}",<#t>
"${(report.policyName!"")?replace('"', '""')}",<#t>
"${(report.policyID!"")?replace('"', '""')}",<#t>
"${(report.reimbursed!"")?replace('"', '""')}",<#t>
"${(report.reportID!"")?replace('"', '""')}",<#t>
"${(report.oldReportID!"")?replace('"', '""')}",<#t>
"${(report.reportName!"")?replace('"', '""')}",<#t>
"${(report.status!"")?replace('"', '""')}",<#t>
"${(report.displayStatus!"")?replace('"', '""')}",<#t>
"${(report.submitted!"")?replace('"', '""')}",<#t>
"${(report.employeeCustomField1!"")?replace('"', '""')}",<#t>
"${(report.employeeCustomField2!"")?replace('"', '""')}",<#t>
"${((report.submitter.firstName)!"")?replace('"', '""')}",<#t>
"${((report.submitter.lastName)!"")?replace('"', '""')}",<#t>
"${((report.submitter.fullName)!"")?replace('"', '""')}",<#t>
"${totalAmount}"<#lt>
</#list>
