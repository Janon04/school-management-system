# How to Add Staff Members in Admin Panel

## Two-Step Process

### Step 1: Create a User Account First
Before adding a staff member, you need to create a user account:

1. Go to: **http://127.0.0.1:8000/admin/accounts/user/add/**
2. Fill in the required fields:
   - **Username**: e.g., `jsmith`
   - **Password**: Create a secure password (type it twice)
   - **Role**: Select "**Staff**" (IMPORTANT!)
   - **Email**: e.g., `john.smith@school.com`
   - **First name**: e.g., `John`
   - **Last name**: e.g., `Smith`
   - **Phone number**: Optional (e.g., `+1234567890`)
3. Click **SAVE**

### Step 2: Create the Staff Profile
After creating the user account:

1. Go to: **http://127.0.0.1:8000/admin/staff/staff/add/**
2. Fill in the required fields:
   - **User**: Start typing the username you just created (e.g., type "jsmith")
     - The autocomplete will show matching users
     - Select the correct user from the dropdown
   - **Employee ID**: e.g., `STAFF001` (must be unique)
   - **Department**: Select from dropdown (Admin, Accounts, Library, etc.)
   - **Designation**: e.g., `Accountant`, `Librarian`, `Lab Assistant`
   - **Joining date**: Select the date they joined
   - **Salary**: Optional (can be left blank)
   - **Is active**: Check this box to activate the staff member
3. Click **SAVE**

## Quick Tips

✅ **Always create the User account FIRST** (with Role = Staff)
✅ **Then create the Staff profile** and link it to the user
✅ The user can now login with their username and password
✅ You can edit both User and Staff profiles anytime

## Common Issues

❌ **"User not found"**: Make sure you created the user account first
❌ **Can't select user**: Make sure the user's role is set to "Staff"
❌ **Duplicate employee ID**: Each staff member needs a unique employee ID

## Example Data

**User Account:**
- Username: `jsmith`
- Password: `SecurePass123!`
- Role: `Staff`
- Email: `john.smith@school.com`
- First Name: `John`
- Last Name: `Smith`

**Staff Profile:**
- User: `jsmith - John Smith`
- Employee ID: `STAFF001`
- Department: `Accounts`
- Designation: `Senior Accountant`
- Joining Date: `2024-01-15`
- Salary: `50000.00`
- Is Active: ✓

## Need Help?

If you still can't add a staff member:
1. Make sure the user account exists in Users section
2. Make sure the user's role is "Staff"
3. Check that the employee ID is unique
4. Refresh the page and try again
