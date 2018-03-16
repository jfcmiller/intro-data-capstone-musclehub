#Capstone project by Jim Miller

# This import only needs to happen once, at the beginning of the notebook
from codecademySQL import sql_query

# Here's an example of a query that just displays some data
sql_query('''
SELECT *
FROM visits
LIMIT 5
''')

# Here's an example where we save the data to a DataFrame
df = sql_query('''
SELECT *
FROM applications
LIMIT 5
''')

# Examine visits here
sql_query('''
SELECT *
FROM visits
where visit_date >= DATE('2017-07-01')
order by visit_date
limit 5
''')

# Examine fitness_tests here
sql_query('''
SELECT *
FROM fitness_tests
limit 5
''')

# Examine applications here
sql_query('''
SELECT *
FROM applications
limit 5
''')


# Examine purchases here
sql_query('''
SELECT *
FROM purchases
limit 5
''')


#This creates a dataframe with the results of a query pulling out desired fields where visit_date
#is on or after July 1, 2017
df = sql_query('''
SELECT visits.first_name,visits.last_name,visits.gender,visits.email,visits.visit_date \
,fitness_tests.fitness_test_date,applications.application_date,purchases.purchase_date
FROM visits
LEFT JOIN fitness_tests on visits.first_name=fitness_tests.first_name \
AND visits.last_name=fitness_tests.last_name \
AND visits.email=fitness_tests.email
LEFT JOIN applications on visits.first_name=applications.first_name \
AND visits.last_name=applications.last_name \
AND visits.email=applications.email
LEFT JOIN purchases on visits.first_name=purchases.first_name \
and visits.last_name=purchases.last_name \
and visits.email=purchases.email
where visits.visit_date>='7-1-17'
ORDER BY visit_date
''')


# ## Step 3: Investigate the A and B groups


import pandas as pd
from matplotlib import pyplot as plt


#This creates ab_test_group field.
#Using a lambda function, ab_test_group will be A if fitness_test_date is not None
#and B if fitness_test_date is None
df['ab_test_group']=df['fitness_test_date'].apply(lambda x: 'A' if pd.notnull(x) else 'B')

print(df.head())


#Show how many users are in each ab_test_group and saves the result as ab_counts 
ab_counts=df.groupby(['ab_test_group']).last_name.count().reset_index()
print ab_counts


#         We'll want to include this information in our presentation.  Let's create a pie cart using `plt.pie`.  Make sure to include:
# - Use `plt.axis('equal')` so that your pie chart looks nice
# - Add a legend labeling `A` and `B`
# - Use `autopct` to label the percentage of each group
# - Save your figure as `ab_test_pie_chart.png`

# In[12]:


#Makes a pie chart showing A and B labels and a test group's percentage of total users. Saves it as a .png
plt.pie(ab_counts.last_name,autopct='%d%%')
plt.legend(['A', 'B'])
plt.axis('equal')
plt.savefig('ab_test_pie_chart.png')


#Creates a new column to categorize whether or not someone filled out an application.
df['is_application']=df['application_date'].apply(lambda x: 'Application' if pd.notnull(x) else 'No Application')
df.head()


#This calculates how many people in group A and group B either do, or don't, pick up an application.
app_counts=df.groupby(['ab_test_group','is_application']).last_name.count().reset_index()
app_counts.head()

#Creating a pivot table on app_counts. Index is ab_test_group and columns are is_application.
app_pivot=app_counts.pivot(columns='is_application',index='ab_test_group',values='last_name').reset_index()
app_pivot.head()


#Creates a new column called total in the app_pivot dataframe. It sums up application and no application.
app_pivot['Total'] = app_pivot['Application']+app_pivot['No Application']
app_pivot.head()



#Creates a 'percent with application' field by dividing 'application' by 'total.' 
#Multiplied by 100.
app_pivot['Percent with Application']=(app_pivot['Application']/app_pivot['Total'])*100
app_pivot.head()


#Running a Chi Square test to evaluate if the percentage of Group B people who turned in an application
#is significant.
from scipy.stats import chi2_contingency
x = [[250,325],[2254,2175]]
_, app_pvalue, _, _ = chi2_contingency(x)
print app_pvalue


#Creating a column identifying whether people who picked up an application ultimately purchased a membership.
df['is_member']=df['purchase_date'].apply(lambda x: 'Member' if pd.notnull(x) else 'Not Member')
df.head()


#Creating a df of just those Musclehub visitors who picked up an application
just_apps=df[(df.is_application == 'Application')]
just_apps.head()


#Doing a groupby to get the number of number of people who applied from groups A and B
#reshaping it with pivot
#and creating 'total' and 'Percent Purchase' fields.
members_counts=just_apps.groupby(['ab_test_group','is_member']).last_name.count().reset_index()
member_pivot=members_counts.pivot(columns='is_member',index='ab_test_group',values='last_name').reset_index()
member_pivot['Total']=member_pivot['Member']+member_pivot['Not Member']
member_pivot['Percent Purchase']=(member_pivot['Member']/member_pivot['Total'])*100
member_pivot.head()


#Using the Chi Square test to determine if the difference in applicants who purchased a membership
#is statistically significant.
w = [[200,250],[50,75]]
_, membership_pvalue, _, _ = chi2_contingency(w)
print membership_pvalue


#Doing a groupby to get the number of all Musclehub visitors from groups A and B who ultimately
#purchased a membership. Reshaping it with pivot
#and creating 'total' and 'Percent Purchase' fields.
all_visitor_memberships=df.groupby(['ab_test_group','is_member']).last_name.count().reset_index()
final_member_pivot=all_visitor_memberships.pivot(columns='is_member',index='ab_test_group',values='last_name').reset_index()
final_member_pivot['Total']=final_member_pivot['Member']+final_member_pivot['Not Member']
final_member_pivot['Percent purchase']=(final_member_pivot['Member']/final_member_pivot['Total'])*100
final_member_pivot.head()


#Using the Chi Square test to determine if the difference in visitors who purchased a membership
#is statistically significant.

y = [[200,250],[2304,2250]]
_, visitor_member_pvalue, _, _ = chi2_contingency(y)
print visitor_member_pvalue



#This shows the percentage of Musclehub visitors who apply for membership
ax = plt.subplot()
plt.bar(range(len(app_pivot)),app_pivot['Percent with Application'])
ax.set_xticks(range(len(app_pivot)))
ax.set_xticklabels(['Fitness Test','No Fitness Test'])
ax.set_yticks([5, 10, 15, 20, 25, 30])
ax.set_yticklabels(['5%','10%','15%','20%','25%','30%'])
plt.savefig('visitors_who_take_app.png')
plt.ylabel('Percentage of visitors who apply')
plt.title('Musclehub visitors who take an application')
plt.show()


#This shows the percentage of applicants who purchase a membership
ax = plt.subplot()
plt.bar(range(len(member_pivot)),member_pivot['Percent Purchase'])
ax.set_xticks(range(len(member_pivot)))
ax.set_xticklabels(['Fitness Test','No Fitness Test'])
ax.set_yticks([10, 20, 30, 40, 50, 60, 70, 80, 90])
ax.set_yticklabels(['10%','20%','30%','40%','50%','60%','70%','80%','90%'])
plt.savefig('applicants_who_buy_membership.png')
plt.ylabel('Percentage of applicants who purchased a membership')
plt.title('Musclehub applicants who purchase a membership')
plt.show()



#This shows the percentage of visitors who purchase a membership
ax = plt.subplot()
plt.bar(range(len(final_member_pivot)),final_member_pivot['Percent purchase'])
ax.set_xticks(range(len(final_member_pivot)))
ax.set_xticklabels(['Fitness Test','No Fitness Test'])
ax.set_yticks([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
ax.set_yticklabels(['1%','2%','3%','4%','5%','6%', '7%', '8%', '9%', '10%'])
plt.savefig('all_visitors_who_buy_membership.png')
plt.ylabel('Percentage of visitors who purchased a membership')
plt.title('Musclehub visitors who purchase a membership')
plt.show()

