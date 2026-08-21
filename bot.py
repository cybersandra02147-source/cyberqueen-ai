import os
import sqlite3
from datetime import datetime

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from subscriptions import (
    PLANS,
    create_pending_subscription,
    set_payment_method,
    get_pending_subscriptions,
    activate_subscription,
    reject_subscription,
    get_subscription,
)

from payment_proofs import (
    save_payment_proof,
    get_pending_proofs,
    mark_proof_verified,
    mark_proof_rejected,
)

from subscriptions import get_active_subscription

from jobs import (
    create_job,
    get_pending_jobs,
    get_job,
    update_job_status,
    get_all_jobs,
    set_generated_folder,
    get_generated_folder,
)

from config import PUBLIC_BASE_URL

from website_generator import generate_website
from site_manager import create_site
from image_generator import generate_logo

from projects import (
    init_projects_db,
    create_project,
    add_project_field,
    update_project_field,
    get_project,
    get_project_fields,
    set_project_status,
)

from telegram.error import BadRequest
# =========================
# BOT TOKEN
# =========================

TOKEN = os.environ.get("TOKEN")
ADMIN_ID = 8737019035

# =========================
# DATABASE
# =========================

def is_admin(user_id):
    return user_id == ADMIN_ID


def save_user(user):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT OR IGNORE INTO users
        (id, first_name, username, chat_id)
        VALUES (?, ?, ?, ?)
        """,
        (
            user.id,
            user.first_name,
            user.username,
            user.id,
        ),
    )

    conn.commit()
    conn.close()


# =========================
# MAIN MENU
# =========================

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        [
            InlineKeyboardButton(
                "🛍 Create Online Shop",
                callback_data="shop"
            )
        ],
        [
            InlineKeyboardButton(
                "🌐 Create Website",
                callback_data="website"
            )
        ],
        [
            InlineKeyboardButton(
                "📋 Create Form",
                callback_data="form"
            )
        ],
        [
            InlineKeyboardButton(
                "🤖 AI Assistant",
                callback_data="ai"
            )
        ],
        [
            InlineKeyboardButton(
                "💳 Payments",
                callback_data="payment"
            )
        ],
        [
            InlineKeyboardButton(
                "👤 My Account",
                callback_data="account"
            )
        ],
        [
            InlineKeyboardButton(
                "📞 Support",
                callback_data="support"
            )
        ],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.effective_chat.send_message(
        text=(
            "🏠 Welcome to CyberQueen AI\n\n"
            "Choose what you want to do:"
        ),
        reply_markup=reply_markup,
    )


async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user

    if not user:
        return

    if not is_admin(user.id):
        await update.effective_chat.send_message(
            "⛔ Access denied.\n\n"
            "This area is restricted to administrators."
        )
        return

    keyboard = [
        [
            InlineKeyboardButton(
                "👥 Users",
                callback_data="admin_users"
            )
        ],
        [
            InlineKeyboardButton(
                "💳 Payments",
                callback_data="admin_payments"
            )
        ],
        [
            InlineKeyboardButton(
                "📞 Support",
                callback_data="admin_support"
            )
        ],
        [
            InlineKeyboardButton(
                "🛍 Shops",
                callback_data="admin_shops"
            )
        ],
    ]

    await update.effective_chat.send_message(
        "👑 ADMIN LOGIN SUCCESSFUL\n\n"
        f"Welcome, {user.first_name}.\n\n"
        "Your administrator account has been detected.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# =========================
# START
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user:
        save_user(update.effective_user)

    # Check whether this user is the administrator
    if update.effective_user and is_admin(update.effective_user.id):

        keyboard = [
            [
                InlineKeyboardButton(
                    "👑 Admin Dashboard",
                    callback_data="admin_dashboard"
                )
            ],
            [
                InlineKeyboardButton(
                    "🏠 User Menu",
                    callback_data="open_menu"
                )
            ]
        ]

        await update.effective_chat.send_message(
            text=(
                "👑 Welcome back, Administrator.\n\n"
                "Your admin account has been detected."
            ),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

        return

    # Normal user menu
    keyboard = [
        [
            InlineKeyboardButton(
                "🚀 Open CyberQueen AI",
                callback_data="open_menu"
            )
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.effective_chat.send_message(
        text=(
            "👋 Welcome!\n\n"
            "I am CyberQueen AI.\n\n"
            "I can help you create websites, "
            "online shops, forms and other digital services."
        ),
        reply_markup=reply_markup,
    )


# =========================
# HELP
# =========================

async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.effective_chat.send_message(
        text=(
            "📋 Available commands:\n\n"
            "/start - Start the bot\n"
            "/menu - Open the main menu\n"
            "/help - Show help\n"
            "/about - About CyberQueen AI\n"
            "/time - Current time\n"
            "/users - Registered users\n"
            "/payment - Payment methods"
        )
    )


# =========================
# ABOUT
# =========================

async def about(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.effective_chat.send_message(
        text=(
            "🤖 CyberQueen AI\n\n"
            "A Python-powered business automation "
            "platform."
        )
    )


# =========================
# TIME
# =========================

async def time_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    now = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    await update.effective_chat.send_message(
        text=f"🕒 Current time:\n{now}"
    )


# =========================
# USERS
# =========================

async def users(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM users"
    )

    total = cursor.fetchone()[0]

    conn.close()

    await update.effective_chat.send_message(
        text=f"👥 Total registered users: {total}"
    )


async def myid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    await update.effective_chat.send_message(
        f"Your Telegram ID is:\n{user.id}"
    )


# =========================
# PAYMENT MENU
# =========================

async def payment(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    keyboard = [
        [
            InlineKeyboardButton(
                "💳 Debit Card",
                callback_data="pay_debit"
            )
        ],
        [
            InlineKeyboardButton(
                "💳 Credit Card",
                callback_data="pay_credit"
            )
        ],
        [
            InlineKeyboardButton(
                "🏦 Bank Transfer",
                callback_data="pay_bank"
            )
        ],
        [
            InlineKeyboardButton(
                "₿ Bitcoin",
                callback_data="pay_bitcoin"
            )
        ],
        [
            InlineKeyboardButton(
                "📱 Mobile Wallet",
                callback_data="pay_wallet"
            )
        ],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.effective_chat.send_message(
        text=(
            "💳 Choose your payment method:\n\n"
            "Select the method that is most convenient "
            "for you."
        ),
        reply_markup=reply_markup,
    )


async def support(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data["waiting_for_support"] = True

    await update.effective_chat.send_message(
        "📞 CyberQueen AI Support\n\n"
        "Tell us what problem you are having.\n\n"
        "You can explain what you were trying to create "
        "and what went wrong.\n\n"
        "A human administrator will review your message."
    )

async def plans(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        [
            InlineKeyboardButton(
                "🗓 $20 — 1 Week",
                callback_data="plan_week"
            )
        ],
        [
            InlineKeyboardButton(
                "📅 $60 — 1 Month",
                callback_data="plan_month"
            )
        ],
        [
            InlineKeyboardButton(
                "📆 $150 — 3 Months",
                callback_data="plan_three_months"
            )
        ]
    ]

    await update.effective_chat.send_message(
        "💎 CYBERQUEEN AI PLANS\n\n"
        "Choose how long you want your services:\n\n"
        "🗓 1 Week — $20\n"
        "📅 1 Month — $60\n"
        "📆 3 Months — $150",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def admin_jobs(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != ADMIN_ID:
        await update.effective_message.reply_text(
            "⛔ Admin access only."
        )
        return

    jobs = get_pending_jobs()

    if not jobs:
        await update.effective_message.reply_text(
            "📋 ADMIN JOB DASHBOARD\n\n"
            "No pending jobs."
        )
        return

    await update.effective_message.reply_text(
        f"👑 ADMIN JOB DASHBOARD\n\n"
        f"📥 Open jobs: {len(jobs)}"
    )

    for job in jobs:

        job_id = job[0]
        user_id = job[1]
        subscription_id = job[2]
        service = job[3]
        description = job[4]
        status = job[5]
        created_at = job[6]

        keyboard = []

        if status == "PENDING":
            keyboard.append([
                InlineKeyboardButton(
                    "🟡 Start",
                    callback_data=f"job_start_{job_id}"
                ),
                InlineKeyboardButton(
                    "❌ Reject",
                    callback_data=f"job_reject_{job_id}"
                )
            ])

        elif status == "IN PROGRESS":
            keyboard.append([
                InlineKeyboardButton(
                    "✅ Complete",
                    callback_data=f"job_complete_{job_id}"
                ),
                InlineKeyboardButton(
                    "❌ Cancel",
                    callback_data=f"job_cancel_{job_id}"
                )
            ])

        await update.effective_message.reply_text(
            "📋 JOB REQUEST\n\n"
            f"Job ID: #{job_id}\n"
            f"User ID: {user_id}\n"
            f"Subscription: #{subscription_id}\n"
            f"Service: {service}\n"
            f"Status: {status}\n"
            f"Created: {created_at}\n\n"
            f"Customer request:\n{description}",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )


# =========================
# BUTTON HANDLER
# =========================

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    data = query.data
    choice = query.data

    # =========================
    # WEBSITE LOGO BUTTONS
    # =========================

    if data.startswith("generate_logo_"):

        project_id = int(data.split("_")[-1])

        context.user_data["project_id"] = project_id
        context.user_data["project_step"] = "logo_generate"

        await query.edit_message_text(
            "🎨 LOGO GENERATOR\n\n"
            "Tell me what you want your logo to look like.\n\n"
            "For example:\n"
            "• Modern fashion logo\n"
            "• Luxury clothing brand\n"
            "• Tech company logo\n"
            "• Simple black and gold logo"
        )

        return


    if data.startswith("skip_logo_"):

        project_id = int(data.split("_")[-1])

        update_project_field(
            project_id,
            "logo",
            None
        )

        await query.edit_message_text(
            "⏭️ Logo skipped.\n\n"
            "Your website information is now complete."
        )

        await finish_website_project(
            update,
            context,
            project_id
        )

        return

    if query.from_user.id != ADMIN_ID:
        await query.answer(
            "Admin access only.",
            show_alert=True
        )
        return


    if data.startswith("job_start_"):

        job_id = int(data.split("_")[-1])
        job = get_job(job_id)

        if not job:
            await query.answer(
                "Job not found.",
                show_alert=True
            )
            return

        user_id = job[1]
        service = job[3]
        description = job[4]

        update_job_status(
            job_id,
            "IN PROGRESS"
        )

        generated_message = ""

        # Generate website automatically
        if service == "Website / Link":

            try:
                project_id = job[7]

                folder, filepath = generate_website(
                    description,
                    job_id,
                    project_id
                )

                set_generated_folder(
                    job_id,
                    folder
                )

                generated_message = (
                    "\n\n🌐 WEBSITE GENERATED\n"
                    f"Folder: {folder}\n"
                    f"File: {filepath}"
                )

            except Exception as error:

                update_job_status(
                    job_id,
                    "FAILED"
                )

                await query.answer(
                    "Website generation failed.",
                    show_alert=True
                )

                await context.bot.send_message(
                    chat_id=ADMIN_ID,
                    text=(
                        "❌ WEBSITE GENERATION FAILED\n\n"
                        f"Job: #{job_id}\n"
                        f"Error: {error}"
                    )
                )

                return

        await context.bot.send_message(
            chat_id=user_id,
            text=(
                f"🟡 JOB #{job_id} STARTED\n\n"
                f"Service: {service}\n\n"
                "Your request is now being processed."
                f"{generated_message}"
            )
        )

        await query.answer(
            "Job started."
        )

        await query.edit_message_reply_markup(
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "✅ Complete",
                        callback_data=f"job_complete_{job_id}"
                    ),
                    InlineKeyboardButton(
                        "❌ Cancel",
                        callback_data=f"job_cancel_{job_id}"
                    )
                ]
            ])
        )

        return


    if data.startswith("job_complete_"):

        job_id = int(data.split("_")[-1])
        job = get_job(job_id)

        if not job:
            await query.answer(
                "Job not found.",
                show_alert=True
            )
            return

        user_id = job[1]
        service = job[3]
        subscription_id = job[2]

        # Website delivery
        if service == "Website / Link":

            if not subscription_id:
                await context.bot.send_message(
                    chat_id=user_id,
                    text=(
                        "❌ This job does not have a valid "
                        "subscription attached."
                    )
                )
                return

            subscription = get_subscription(
                subscription_id
            )

            if not subscription:
                await context.bot.send_message(
                    chat_id=user_id,
                    text=(
                        "❌ Subscription could not be found."
                    )
                )
                return

            expires_at = subscription[7]

            folder = None

            # Find the generated website folder
            import os

            folder = get_generated_folder(job_id)

            if not folder:
                await context.bot.send_message(
                    chat_id=user_id,
                    text=(
                        "❌ The generated website could not be "
                        "located for this job."
                     )
                )
                return

            if not folder:
                await context.bot.send_message(
                    chat_id=user_id,
                    text=(
                        "❌ The generated website "
                        "could not be found."
                    )
                )
                return

            site_id, site_key = create_site(
                user_id=user_id,
                job_id=job_id,
                subscription_id=subscription_id,
                folder=folder,
                expires_at=expires_at
            )

            website_url = f"{PUBLIC_BASE_URL}/site/{site_key}/"

            await context.bot.send_message(
                chat_id=user_id,
                text=(
                    f"✅ JOB #{job_id} COMPLETED\n\n"
                    "🌐 Your website has been generated successfully.\n\n"
                    f"⏳ Active until:\n{expires_at}\n\n"
                    "Tap the button below to open your website in Chrome."
                ),
                reply_markup=InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton(
                            "🌐 Open Website",
                            url=website_url
                        )
                    ]
                ])
             )

        else:

            await context.bot.send_message(
                chat_id=user_id,
                text=(
                    f"✅ JOB #{job_id} COMPLETED\n\n"
                    f"Service: {service}\n\n"
                    "Your request has been completed."
                )
            )

        update_job_status(job_id, "COMPLETED")

        try:
            await query.edit_message_reply_markup(
                reply_markup=None
            )
        except BadRequest:
            pass


    if data.startswith("job_reject_"):

        job_id = int(data.split("_")[-1])
        job = get_job(job_id)

        if not job:
            await query.answer(
                "Job not found.",
                show_alert=True
            )
            return

        update_job_status(job_id, "REJECTED")

        user_id = job[1]

        await context.bot.send_message(
            chat_id=user_id,
            text=(
                f"❌ JOB #{job_id} REJECTED\n\n"
                "Your request could not be accepted."
            )
        )

        await query.answer("Job rejected.")

        await query.edit_message_reply_markup(
            reply_markup=None
        )

        return


    if data.startswith("job_cancel_"):

        job_id = int(data.split("_")[-1])
        job = get_job(job_id)

        if not job:
            await query.answer(
                "Job not found.",
                show_alert=True
            )
            return

        update_job_status(job_id, "CANCELLED")

        user_id = job[1]

        await context.bot.send_message(
            chat_id=user_id,
            text=(
                f"❌ JOB #{job_id} CANCELLED\n\n"
                "Your request has been cancelled."
            )
        )

        await query.answer("Job cancelled.")

        await query.edit_message_reply_markup(
            reply_markup=None
        )

        return

    # Open main menu
    if data == "open_menu":

        keyboard = [
            [
                InlineKeyboardButton(
                    "🛍 Create Online Shop",
                    callback_data="shop"
                )
            ],
            [
                InlineKeyboardButton(
                    "🌐 Create Website",
                    callback_data="website"
                )
            ],
            [
                InlineKeyboardButton(
                    "📋 Create Form",
                    callback_data="form"
                )
            ],
            [
                InlineKeyboardButton(
                    "🤖 AI Assistant",
                    callback_data="ai"
                )
            ],
            [
                InlineKeyboardButton(
                    "💳 Payments",
                    callback_data="payment"
                )
            ],
            [
                InlineKeyboardButton(
                    "👤 My Account",
                    callback_data="account"
                )
            ],
            [
                InlineKeyboardButton(
                    "📞 Support",
                    callback_data="support"
                )
            ],
        ]

        await query.edit_message_text(
            text=(
                "🏠 CyberQueen AI\n\n"
                "Choose a service:"
            ),
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

        # Online shop
    elif choice == "shop":

        keyboard = [
            [
                InlineKeyboardButton(
                    "💳 Choose Payment Method",
                    callback_data="shop_payment"
                )
            ],
            [
                InlineKeyboardButton(
                    "❌ Cancel",
                    callback_data="open_menu"
                )
            ]
        ]

        await query.edit_message_text(
            text=(
                "🛍️ ONLINE SHOP\n\n"
                "Price: $20 USD\n\n"
                "Your shop will include:\n"
                "✅ Products\n"
                "✅ Prices\n"
                "✅ Shopping cart\n"
                "✅ Customer pages\n"
                "✅ Business information\n\n"
                "Payment must be verified before "
                "your shop is generated.\n\n"
                "Choose how you want to pay:"
            ),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # Website
    elif choice == "website":

        await query.edit_message_text(
            text=(
                "🌐 BUSINESS WEBSITE\n\n"
                "Price: $15\n\n"
                "We will collect your business details "
                "and generate your website after payment "
                "is verified."
            )
        )

    # Form
    elif choice == "form":

        await query.edit_message_text(
            text=(
                "📋 FORM BUILDER\n\n"
                "Price: $5\n\n"
                "You can create forms for collecting "
                "customer or business information."
            )
        )

    # AI
    elif choice == "ai":

        await query.edit_message_text(
            text=(
                "🤖 AI ASSISTANT\n\n"
                "Price: $10/month\n\n"
                "The AI assistant will help with "
                "business tasks and other supported "
                "requests."
            )
        )

    # Payment menu
    elif choice == "payment":

        keyboard = [
            [
                InlineKeyboardButton(
                    "💳 Debit Card",
                    callback_data="pay_debit"
                )
            ],
            [
                InlineKeyboardButton(
                    "💳 Credit Card",
                    callback_data="pay_credit"
                )
            ],
            [
                InlineKeyboardButton(
                    "🏦 Bank Transfer",
                    callback_data="pay_bank"
                )
            ],
            [
                InlineKeyboardButton(
                    "₿ Bitcoin",
                    callback_data="pay_bitcoin"
                )
            ],
            [
                InlineKeyboardButton(
                    "📱 Mobile Wallet",
                    callback_data="pay_wallet"
                )
            ],
        ]

        await query.edit_message_text(
            text="💳 Choose your payment method:",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )


    elif choice == "shop_payment":

        keyboard = [
            [
                InlineKeyboardButton(
                    "💳 Debit Card",
                    callback_data="pay_debit"
                )
            ],
            [
                InlineKeyboardButton(
                    "💳 Credit Card",
                    callback_data="pay_credit"
                )
            ],
            [
                InlineKeyboardButton(
                    "🏦 Bank Transfer",
                    callback_data="pay_bank"
                )
            ],
            [
                InlineKeyboardButton(
                    "₿ Bitcoin",
                    callback_data="pay_bitcoin"
                )
            ],
            [
                InlineKeyboardButton(
                    "📱 Mobile Wallet",
                    callback_data="pay_wallet"
                )
            ]
        ]

        await query.edit_message_text(
            text=(
                "💳 PAYMENT METHOD\n\n"
                "Online Shop — $20 USD\n\n"
                "Choose your preferred payment method:"
            ),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif choice == "admin_users":

        if query.from_user.id != ADMIN_ID:
            await query.answer(
                "⛔ Not authorized.",
                show_alert=True
            )
            return

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]

        conn.close()

        await query.edit_message_text(
            f"👥 USERS\n\n"
            f"Total registered users: {total_users}"
        )

    elif choice == "admin_support":

        if query.from_user.id != ADMIN_ID:
            await query.answer(
                "⛔ Not authorized.",
                show_alert=True
            )
            return

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, first_name, username, message, status
            FROM support_tickets
            WHERE status = 'OPEN'
            ORDER BY id DESC
        """)

        tickets = cursor.fetchall()
        conn.close()

        if not tickets:
            await query.edit_message_text(
                "📞 SUPPORT\n\n"
                "No open support tickets."
            )
            return

        text = "📞 OPEN SUPPORT TICKETS\n\n"

        for ticket in tickets:
            ticket_id, first_name, username, message, status = ticket

            text += (
                f"🎫 Ticket #{ticket_id}\n"
                f"User: {first_name}\n"
                f"Username: @{username or 'none'}\n"
                f"Status: {status}\n"
                f"Message: {message}\n\n"
            )

        await query.edit_message_text(text)

    # Account
    elif choice == "account":

        await query.edit_message_text(
            text=(
                "👤 MY ACCOUNT\n\n"
                "Your account dashboard will be "
                "available here."
            )
        )

    elif choice == "admin_payments":

        if not is_admin(query.from_user.id):
            await query.answer(
                "⛔ Not authorized.",
                show_alert=True
            )
            return

        pending = get_pending_subscriptions()

        if not pending:
            await query.edit_message_text(
                "💳 PAYMENT REQUESTS\n\n"
                "No pending payments."
            )
            return

        for payment in pending:

            (
                subscription_id,
                user_id,
                plan,
                amount,
                currency,
                payment_method,
                status,
                started_at,
                expires_at
            ) = payment

            keyboard = [
                [
                    InlineKeyboardButton(
                        "✅ Approve",
                        callback_data=f"approve_payment:{subscription_id}"
                    ),
                    InlineKeyboardButton(
                        "❌ Reject",
                        callback_data=f"reject_payment:{subscription_id}"
                    )
                ]
            ]

            await query.message.reply_text(
                f"🔴 PAYMENT #{subscription_id}\n\n"
                f"User ID: {user_id}\n"
                f"Plan: {plan}\n"
                f"Amount: {amount:.2f} {currency}\n"
                f"Method: {payment_method or 'Not selected'}\n"
                f"Status: {status}",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

        # Support
    elif choice == "support":

        context.user_data["waiting_for_support"] = True

        await query.edit_message_text(
            text=(
                "📞 CYBERQUEEN AI SUPPORT\n\n"
                "Having a problem?\n\n"
                "Tell us what you are trying to do "
                "and explain what went wrong.\n\n"
                "A human administrator will review "
                "your request and reply here."
            )
        )

    elif choice == "admin_dashboard":

        if not is_admin(query.from_user.id):
            await query.answer(
                "⛔ Not authorized.",
                show_alert=True
            )
            return

        keyboard = [
            [
                InlineKeyboardButton(
                    "👥 Users",
                    callback_data="admin_users"
                )
            ],
            [
                InlineKeyboardButton(
                    "💳 Payments",
                    callback_data="admin_payments"
                )
            ],
            [
                InlineKeyboardButton(
                    "📞 Support",
                    callback_data="admin_support"
                )
            ],
            [
                InlineKeyboardButton(
                    "🛍 Shops",
                    callback_data="admin_shops"
                )
            ]
        ]

        await query.edit_message_text(
            "👑 CYBERQUEEN ADMIN DASHBOARD\n\n"
            "Administrator verified.\n\n"
            "Choose an option:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # Pazyment methods
    elif choice == "pay_debit":

        await query.edit_message_text(
            text=(
                "💳 DEBIT CARD\n\n"
                "Card checkout will be connected "
                "through a secure payment provider.\n\n"
                "We will never ask you to send your "
                "card number, CVV or PIN to this bot."
            )
        )

    elif choice == "pay_credit":

        await query.edit_message_text(
            text=(
                "💳 CREDIT CARD\n\n"
                "Secure card checkout will be connected "
                "through a payment provider."
            )
        )

    elif choice == "pay_bank":

        await query.edit_message_text(
            text=(
                "🏦 BANK TRANSFER\n\n"
                "Bank transfer details will appear here.\n\n"
                "After payment, the customer will submit "
                "the transaction reference and receipt "
                "for verification."
            )
        )

    elif choice == "pay_bitcoin":

        await query.edit_message_text(
            text=(
                "₿ BITCOIN\n\n"
                "Bitcoin payment will be connected "
                "through a secure crypto payment system."
            )
        )

    elif choice == "pay_wallet":

        await query.edit_message_text(
            text=(
                "📱 MOBILE WALLET\n\n"
                "Available mobile-wallet options will "
                "depend on the customer's country."
            )
        )

    elif choice.startswith("plan_"):

        plan_key = choice.replace("plan_", "")

        if plan_key not in PLANS:
            await query.answer(
                "Invalid plan.",
                show_alert=True
            )
            return

        plan = PLANS[plan_key]

        subscription_id = create_pending_subscription(
            user_id=query.from_user.id,
            plan_key=plan_key
        )

        keyboard = [
            [
                InlineKeyboardButton(
                    "💳 Choose Payment Method",
                    callback_data=f"subscription_payment:{subscription_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    "❌ Cancel",
                    callback_data="open_menu"
                )
            ]
        ]

        await query.edit_message_text(
            f"💎 {plan['name']} PLAN\n\n"
            f"Price: ${plan['amount']:.2f} USD\n"
            f"Duration: {plan['days']} days\n\n"
            "Choose your payment method to continue.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )


    elif choice.startswith("subscription_payment:"):

        subscription_id = choice.split(":")[1]

        keyboard = [
            [
                InlineKeyboardButton(
                    "💳 Debit Card",
                    callback_data=f"subpay_debit:{subscription_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    "💳 Credit Card",
                    callback_data=f"subpay_credit:{subscription_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    "🏦 Bank Transfer",
                    callback_data=f"subpay_bank:{subscription_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    "₿ Bitcoin",
                    callback_data=f"subpay_bitcoin:{subscription_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    "📱 Mobile Wallet",
                    callback_data=f"subpay_wallet:{subscription_id}"
                )
            ]
        ]

        await query.edit_message_text(
            "💳 PAYMENT METHOD\n\n"
            "Choose your preferred payment method:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif choice.startswith("subpay_"):

        parts = choice.split(":")

        if len(parts) != 2:
            await query.answer(
                "Invalid payment request.",
                show_alert=True
            )
            return

        payment_type = parts[0].replace("subpay_", "")
        subscription_id = parts[1]

        payment_names = {
            "debit": "Debit Card",
            "credit": "Credit Card",
            "bank": "Bank Transfer",
            "bitcoin": "Bitcoin",
            "wallet": "Mobile Wallet"
        }

        payment_method = payment_names.get(payment_type)

        if payment_method is None:
            await query.answer(
                "Invalid payment method.",
                show_alert=True
            )
            return

        set_payment_method(
            subscription_id,
            payment_method
        )

        # CARD PAYMENT

        if payment_method in ["Debit Card", "Credit Card"]:

            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=(
                    "💳 CARD PAYMENT REQUEST\n\n"
                    f"Subscription ID: #{subscription_id}\n"
                    f"User ID: {query.from_user.id}\n"
                    f"Name: {query.from_user.first_name}\n"
                    f"Method: {payment_method}\n\n"
                    "Status: ⏳ PENDING\n\n"
                    "Customer selected card payment."
                )
            )

            keyboard = [
                [
                    InlineKeyboardButton(
                        "👑 Contact Payment Admin",
                        url=f"tg://user?id={ADMIN_ID}"
                    )
                ]
            ]

            await query.edit_message_text(
                f"💳 {payment_method} PAYMENT\n\n"
                "Your payment request has been created.\n\n"
                "Please contact our payment administrator "
                "for the secure payment checkout.\n\n"
                "Your subscription will remain PENDING "
                "until payment is verified.\n\n"
                "⚠️ Never send your card number, CVV, PIN, "
                "OTP or banking password to this bot.",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

        # BANK TRANSFER

        elif payment_method == "Bank Transfer":

            await query.edit_message_text(
                "🏦 BANK TRANSFER\n\n"
                "Your payment request has been created.\n\n"
                "Payment status: ⏳ PENDING\n\n"
                "After making the payment, send your "
                "transaction reference and payment receipt.\n\n"
                "An administrator will verify the payment."
            )

        # BITCOIN

        elif payment_method == "Bitcoin":

            await query.edit_message_text(
                "₿ BITCOIN PAYMENT\n\n"
                "Your payment request has been created.\n\n"
                "Payment status: ⏳ PENDING\n\n"
                "Bitcoin payment instructions will be "
                "provided through the payment system."
            )

        # MOBILE WALLET

        elif payment_method == "Mobile Wallet":

            await query.edit_message_text(
                "📱 MOBILE WALLET PAYMENT\n\n"
                "Your payment request has been created.\n\n"
                "Payment status: ⏳ PENDING\n\n"
                "Available wallet options will depend "
                "on the customer's country.\n\n"
                "After payment, submit the transaction "
                "reference and receipt."
            )

    elif choice.startswith("approve_payment:"):

        if not is_admin(query.from_user.id):
            await query.answer(
                "⛔ Not authorized.",
                show_alert=True
            )
            return

        subscription_id = int(
            choice.split(":")[1]
        )

        subscription = get_subscription(subscription_id)

        if not subscription:
            await query.answer(
                "Payment not found.",
                show_alert=True
            )
            return

        activate_subscription(subscription_id)

        user_id = subscription[1]

        await context.bot.send_message(
            chat_id=user_id,
            text=(
                "✅ PAYMENT APPROVED\n\n"
                "Your CyberQueen AI subscription is now active.\n\n"
                f"Plan: {subscription[2]}\n"
                f"Amount: {subscription[3]:.2f} "
                f"{subscription[4]}\n\n"
                "Your paid services are now available."
            )
        )

        await query.edit_message_text(
            f"✅ PAYMENT #{subscription_id} APPROVED\n\n"
            f"User ID: {user_id}\n"
            f"Plan: {subscription[2]}\n"
            f"Status: ACTIVE"
        )

    elif choice.startswith("reject_payment:"):

        if not is_admin(query.from_user.id):
            await query.answer(
                "⛔ Not authorized.",
                show_alert=True
            )
            return

        subscription_id = int(
            choice.split(":")[1]
        )

        subscription = get_subscription(subscription_id)

        if not subscription:
            await query.answer(
                "Payment not found.",
                show_alert=True
            )
            return

        reject_subscription(subscription_id)

        user_id = subscription[1]

        await context.bot.send_message(
            chat_id=user_id,
            text=(
                "❌ PAYMENT NOT APPROVED\n\n"
                "Your payment request was not approved.\n"
                "Please contact support if you believe this "
                "was a mistake."
            )
        )

        await query.edit_message_text(
            f"❌ PAYMENT #{subscription_id} REJECTED\n\n"
            f"User ID: {user_id}\n"
            f"Status: REJECTED"
        )

    elif choice == "service_website":

        await query.answer()

        user_id = query.from_user.id

        project_id = create_project(
            user_id=user_id,
            project_type="WEBSITE",
            description=""
        )

        context.user_data.clear()

        context.user_data["project_id"] = project_id
        context.user_data["project_type"] = "WEBSITE"
        context.user_data["project_step"] = "business_name"

        await query.edit_message_text(
            "🌐 WEBSITE BUILDER\n\n"
            f"Project #{project_id}\n\n"
            "Let's build your website step by step.\n\n"
            "First, what is the name of your "
            "business, brand, shop, or project?"
        )


    elif choice == "service_form":

        context.user_data["job_service"] = "Business Form"
        context.user_data["job_step"] = "description"

        await query.edit_message_text(
            "📝 BUSINESS FORM REQUEST\n\n"
            "Tell me what information you want your customers "
            "to provide.\n\n"
            "Example:\n"
            "I need a customer registration form with name, "
            "phone, email, address and product selection.\n\n"
            "Send the description in your next message."
        )


    elif choice == "service_image":

        context.user_data["job_service"] = "Image Service"
        context.user_data["job_step"] = "description"

        await query.edit_message_text(
            "🖼 IMAGE REQUEST\n\n"
            "Describe the image you want to create or edit.\n\n"
            "Include the style, subject, background and "
            "other details you want.\n\n"
            "Send the description in your next message."
        )


    elif choice == "service_video":

        context.user_data["job_service"] = "Video Service"
        context.user_data["job_step"] = "description"

        await query.edit_message_text(
            "🎬 VIDEO REQUEST\n\n"
            "Describe the business video you want.\n\n"
            "Include the purpose, style, duration, language "
            "and any text or script you want included.\n\n"
            "Send the description in your next message."
        )


    elif choice == "service_ai":

        context.user_data["job_service"] = "AI Assistant"
        context.user_data["job_step"] = "description"

        await query.edit_message_text(
            "🤖 AI ASSISTANT REQUEST\n\n"
            "Tell me what you want CyberQueen AI to do.\n\n"
            "Describe the task as clearly as possible.\n\n"
            "Send your request in your next message."
        )

# =========================
# NORMAL MESSAGES
# =========================
async def services(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    subscription = get_active_subscription(user_id)

    # Allow admin to test services without a subscription
    if not subscription and not is_admin(user_id):
        await update.effective_message.reply_text(
            "🔒 SERVICES LOCKED\n\n"
            "You don't currently have an active subscription.\n\n"
            "Use /plans to choose a plan and activate "
            "your account."
        )
        return

    keyboard = [
        [
            InlineKeyboardButton(
                "🌐 Website / Link",
                callback_data="service_website"
            )
        ],
        [
            InlineKeyboardButton(
                "📝 Business Form",
                callback_data="service_form"
            )
        ],
        [
            InlineKeyboardButton(
                "🖼 Image Service",
                callback_data="service_image"
            )
        ],
        [
            InlineKeyboardButton(
                "🎬 Video Service",
                callback_data="service_video"
            )
        ],
        [
            InlineKeyboardButton(
                "🤖 AI Assistant",
                callback_data="service_ai"
            )
        ],
        [
            InlineKeyboardButton(
                "📞 Support",
                callback_data="support"
            )
        ]
    ]

    if subscription:
        subscription_info = (
            "Your subscription is active.\n\n"
            f"Plan: {subscription[1]}\n"
            f"Expires: {subscription[5]}\n\n"
        )
    else:
        subscription_info = (
            "Admin testing mode is active.\n"
            "You can test the services without a subscription.\n\n"
        )

    await update.effective_message.reply_text(
        "🚀 CYBERQUEEN AI SERVICES\n\n"
        + subscription_info
        + "Choose a service:",
    reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def request_service(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    subscription = get_active_subscription(user_id)

    if not subscription and not is_admin(user_id):
        await update.effective_message.reply_text(
            "🔒 Your subscription is not active.\n\n"
            "Use /plans to choose a plan."
        )
        return

    await update.effective_message.reply_text(
        "📝 NEW SERVICE REQUEST\n\n"
        "Tell me what you want CyberQueen AI to do.\n\n"
        "Example:\n"
        "Create a fashion business website called "
        "Sandra Fashion with Home, Products, About "
        "and Contact pages.\n\n"
        "Send your request in your next message."
    )

    context.user_data["waiting_for_job"] = True
    if subscription:
        context.user_data["subscription_id"] = subscription[0]
    else:
        context.user_data["subscription_id"] = None


async def receive_service_request(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    if await receive_project_message(update, context):
        return

    # your existing code continues here

    job_service = context.user_data.get("job_service")
    job_step = context.user_data.get("job_step")

    if not job_service or job_step != "description":
        return

    user_id = update.effective_user.id
    description = update.effective_message.text

    subscription = get_active_subscription(user_id)

    if not subscription:
        context.user_data.clear()

        await update.effective_message.reply_text(
            "🔒 Your subscription is no longer active.\n\n"
            "Use /plans to choose a new plan."
        )
        return

    subscription_id = subscription[0]

    job_id = create_job(
        user_id=user_id,
        subscription_id=subscription_id,
        service=job_service,
        description=description
    )

    context.user_data.clear()

    await update.effective_message.reply_text(
        "✅ REQUEST RECEIVED\n\n"
        f"Job ID: #{job_id}\n"
        f"Service: {job_service}\n\n"
        "Your request has been sent to the processing "
        "queue.\n\n"
        "You will receive an update when your request "
        "is being processed."
    )

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=(
            "📥 NEW SERVICE REQUEST\n\n"
            f"Job ID: #{job_id}\n"
            f"User ID: {user_id}\n"
            f"Subscription: #{subscription_id}\n"
            f"Service: {job_service}\n\n"
            f"Customer request:\n{description}"
        )
    )

# =========================
# PROJECT BUILDER
# =========================

async def start_website_project(update, context):

    user_id = update.effective_user.id

    project_id = create_project(
        user_id=user_id,
        project_type="WEBSITE",
        description=""
    )

    context.user_data.clear()

    context.user_data["project_id"] = project_id
    context.user_data["project_type"] = "WEBSITE"
    context.user_data["project_step"] = "business_name"

    await update.effective_message.reply_text(
        "🌐 WEBSITE BUILDER\n\n"
        "Let's create your website.\n\n"
        "First, what is the name of your "
        "business, brand, or project?"
    )


async def receive_project_message(update, context):

    project_id = context.user_data.get("project_id")
    project_step = context.user_data.get("project_step")

    if not project_id or not project_step:
        return False

    message = update.effective_message

    # =========================
    # LOGO IMAGE UPLOAD
    # =========================

    if project_step == "logo" and message.photo:

        try:
            photo = message.photo[-1]

            file = await context.bot.get_file(
                photo.file_id
            )

            import os

            logo_dir = "uploaded_logos"

            os.makedirs(
                logo_dir,
                exist_ok=True
            )

            logo_path = os.path.join(
                logo_dir,
                f"project_{project_id}_logo.jpg"
            )

            await file.download_to_drive(
                logo_path
            )

            update_project_field(
                project_id,
                "logo",
                logo_path
            )

            await message.reply_text(
                "✅ Logo uploaded successfully.\n\n"
                "Your website information is now complete."
            )

            await finish_website_project(
                update,
                context,
                project_id
            )

            return True

        except Exception as error:

            await message.reply_text(
                "❌ I could not save the logo.\n\n"
                f"Error: {error}"
            )

            return True

    # =========================
    # NORMAL TEXT MESSAGE
    # =========================

    text = message.text

    if not text:
        return True

    text = text.strip()

    if project_step == "business_name":

        update_project_field(
            project_id,
            "business_name",
            text
        )

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE projects
            SET business_name = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (text, project_id)
        )

        conn.commit()
        conn.close()

        add_project_field(
            project_id,
            "phone",
            required=True
        )

        context.user_data["project_step"] = "phone"

        await update.effective_message.reply_text(
            "Good.\n\n"
            "📱 What phone number should customers "
            "use to contact you?\n\n"
            "You can also type:\n"
            "• I'll add it later"
        )

        return True

    if project_step == "phone":

        if text.lower() in (
            "i'll add it later",
            "ill add it later",
            "later",
            "skip",
            "i don't have it",
            "i dont have it"
        ):
            update_project_field(
                project_id,
                "phone",
                None
            )
        else:
            update_project_field(
                project_id,
                "phone",
                text
            )

        add_project_field(
            project_id,
            "whatsapp",
            required=False
        )

        context.user_data["project_step"] = "whatsapp"

        await update.effective_message.reply_text(
            "📲 Do you want a WhatsApp contact number "
            "on the website?\n\n"
            "Send the number, or type "
            "\"I'll add it later\"."
        )

        return True

    if project_step == "whatsapp":

        if text.lower() not in (
            "i'll add it later",
            "ill add it later",
            "later",
            "skip",
            "i don't have it",
            "i dont have it"
        ):
            update_project_field(
                project_id,
                "whatsapp",
                text
            )

        add_project_field(
            project_id,
            "email",
            required=False
        )

        context.user_data["project_step"] = "email"

        await update.effective_message.reply_text(
            "📧 What email address should appear "
            "on the website?\n\n"
            "Or type \"I'll add it later\"."
        )

        return True

    if project_step == "email":

        if text.lower() not in (
            "i'll add it later",
            "ill add it later",
            "later",
            "skip",
            "i don't have it",
            "i dont have it"
        ):
            update_project_field(
                project_id,
                "email",
                text
            )

        add_project_field(
            project_id,
            "location",
            required=False
        )

        context.user_data["project_step"] = "location"

        await update.effective_message.reply_text(
            "📍 Where is the business located?\n\n"
            "For example:\n"
            "Lagos, Nigeria\n\n"
            "Or type \"I'll add it later\"."
        )

        return True

    if project_step == "location":

        if text.lower() not in (
            "i'll add it later",
            "ill add it later",
            "later",
            "skip"
        ):
            update_project_field(
                project_id,
                "location",
                text
            )

        add_project_field(
            project_id,
            "services",
            required=True
        )

        context.user_data["project_step"] = "services"

        await update.effective_message.reply_text(
            "🛍️ What products or services do you offer?\n\n"
            "Describe them in your own words."
        )

        return True

    if project_step == "services":

        update_project_field(
            project_id,
            "services",
            text
        )

        add_project_field(
            project_id,
            "about",
            required=False
        )

        context.user_data["project_step"] = "about"

        await update.effective_message.reply_text(
            "📝 Tell me a little about the business.\n\n"
            "For example, when you started, what makes "
            "you different, and what customers should know.\n\n"
            "Or type \"I'll add it later\"."
        )

        return True

    if project_step == "about":

        if text.lower() not in (
            "i'll add it later",
            "ill add it later",
            "later",
            "skip"
        ):
            update_project_field(
                project_id,
                "about",
                text
            )

        add_project_field(
            project_id,
            "logo",
            required=False
        )

        context.user_data["project_step"] = "logo"

        await update.effective_message.reply_text(
            "🖼️ Do you have a logo?\n\n"
            "You can upload your own logo, generate one with CyberQueen AI, "
            "or continue without a logo.",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "🎨 Generate a Logo",
        callback_data=f"generate_logo_{project_id}"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "⏭️ Add Later",
        callback_data=f"skip_logo_{project_id}"
                    )
                ]
            ])
        )

        return True

    if project_step == "logo":

        # =========================
        # LOGO IMAGE UPLOAD
        # =========================

        if update.effective_message.photo:

            try:
                photo = update.effective_message.photo[-1]

                file = await context.bot.get_file(
                    photo.file_id
                )

                logo_dir = "uploaded_logos"

                import os

                os.makedirs(
                    logo_dir,
                    exist_ok=True
                )

                logo_path = os.path.join(
                    logo_dir,
                    f"project_{project_id}_logo.jpg"
                )

                await file.download_to_drive(
                    logo_path
                )

                update_project_field(
                    project_id,
                    "logo",
                    logo_path
                )

                await update.effective_message.reply_text(
                    "✅ Logo uploaded successfully.\n\n"
                    "Your website information is now complete."
                )

                await finish_website_project(
                    update,
                    context,
                    project_id
                )

                return True

            except Exception as error:

                await update.effective_message.reply_text(
                    "❌ I could not save the logo.\n\n"
                    f"Error: {error}"
                )

                return True

        if text.lower() in (
            "generate a logo",
            "generate logo",
            "create a logo",
            "make a logo",
            "generate"
        ):

            context.user_data["project_step"] = "logo_generate"

            await message.reply_text(
                "🎨 LOGO GENERATOR\n\n"
                "Describe the logo you want me to create.\n\n"
                "Example:\n"
                "Modern luxury fashion logo for "
                "Sandra Fashion, black and gold, "
                "clean professional design."
            )

            return True

        # =========================
        # LOGO SKIP
        # =========================

        if text.lower() in (
            "i'll add it later",
            "ill add it later",
            "later",
            "skip",
            "no"
        ):

            update_project_field(
                project_id,
                "logo",
                None
            )

            await finish_website_project(
                update,
                context,
                project_id
            )

            return True


        await update.effective_message.reply_text(
            "Please upload the logo as an image, "
            "or type \"I'll add it later\"."
        )

    if project_step == "logo_generate":

        prompt = text.strip()

        if not prompt:
            await message.reply_text(
                "Please describe the logo you want me to create."
            )
            return True

        await message.reply_text(
            "🎨 Creating your logo...\n\n"
            "Please wait while CyberQueen AI generates it."
        )

        try:

            import os

            logo_dir = "uploaded_logos"

            os.makedirs(
                logo_dir,
                exist_ok=True
            )

            logo_path = os.path.join(
                logo_dir,
                f"project_{project_id}_generated.jpg"
            )

            generate_logo(
                prompt,
                logo_path
            )

            update_project_field(
                project_id,
                "logo",
                logo_path
            )

            await message.reply_text(
                "✅ Your logo has been generated successfully.\n\n"
                "I'm now using it for your website."
            )

            await finish_website_project(
                update,
                context,
                project_id
            )

            return True

        except Exception as error:

            await message.reply_text(
                "❌ I couldn't generate the logo.\n\n"
                "Please try again with a different description.\n\n"
                f"Error: {error}"
            )

            return True

        return True


async def finish_website_project(
    update,
    context,
    project_id
):

    set_project_status(
        project_id,
        "READY"
    )

    project = get_project(project_id)
    fields = get_project_fields(project_id)

    if not project:
        await update.effective_message.reply_text(
            "❌ Project could not be found."
        )
        context.user_data.clear()
        return

    user_id = project[1]
    business_name = project[3] or "My Business"
    description = project[4] or ""

    # Build a structured description for the existing job system
    field_data = {}

    for field in fields:
        field_name, field_value, required, status = field
        field_data[field_name] = field_value

    description_parts = [
        f"Business name: {business_name}"
    ]

    for field_name in (
        "phone",
        "whatsapp",
        "email",
        "location",
        "services",
        "about"
    ):
        value = field_data.get(field_name)

        if value:
            description_parts.append(
                f"{field_name.title()}: {value}"
            )

    if description:
        description_parts.append(
            f"Original description: {description}"
        )

    full_description = "\n".join(description_parts)

    # Find the user's active subscription
    subscription = get_active_subscription(user_id)

    if not subscription:
        await update.effective_message.reply_text(
            "⚠️ Your subscription is no longer active.\n\n"
            "Please renew your subscription before "
            "the website can be processed."
        )

        context.user_data.clear()
        return

    subscription_id = subscription[0]

    # Create a job connected to this project
    job_id = create_job(
        user_id=user_id,
        subscription_id=subscription_id,
        service="Website / Link",
        description=full_description,
        project_id=project_id
    )

    summary = []

    for field in fields:
        field_name, field_value, required, status = field

        if field_value:
            summary.append(
                f"• {field_name}: {field_value}"
            )
        else:
            summary.append(
                f"• {field_name}: Will be added later"
            )

    await update.effective_message.reply_text(
        "✅ WEBSITE REQUEST RECEIVED\n\n"
        f"Project #{project_id}\n"
        f"Job #{job_id}\n\n"
        + "\n".join(summary)
        + "\n\n"
        "Your website has been added to the processing "
        "queue.\n\n"
        "An administrator will review and generate it."
    )

    # Notify admin
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=(
            "🌐 NEW WEBSITE PROJECT\n\n"
            f"Project: #{project_id}\n"
            f"Job: #{job_id}\n"
            f"User ID: {user_id}\n"
            f"Subscription: #{subscription_id}\n\n"
            f"Business: {business_name}\n\n"
            f"Website information:\n"
            f"{full_description}"
        )
    )

    context.user_data.clear()


# =========================
# MAIN
# =========================

def main():

    init_projects_db()

    app = Application.builder().token(TOKEN).build()

    app.add_handler(
        CommandHandler("start", start)
    )

    app.add_handler(
        CommandHandler("menu", menu)
    )

    app.add_handler(
        CommandHandler("help", help_command)
    )

    app.add_handler(
        CommandHandler("about", about)
    )

    app.add_handler(
        CommandHandler("time", time_command)
    )

    app.add_handler(
        CommandHandler("users", users)
    )

    app.add_handler(
        CommandHandler("payment", payment)
    )

    app.add_handler(
        CommandHandler("myid", myid)
    )

    app.add_handler(
        CommandHandler("support", support)
    )

    app.add_handler(
        CommandHandler("admin", admin)
    )

    app.add_handler(
        CommandHandler("plans", plans)
    )

    app.add_handler(
        CommandHandler("services", services)
    )

    app.add_handler(
        CommandHandler("request", request_service)
    )

    app.add_handler(
        CommandHandler("jobs", admin_jobs)
    )

    app.add_handler(
        CallbackQueryHandler(button)
    )

    app.add_handler(
        MessageHandler(
            (filters.TEXT | filters.PHOTO) & ~filters.COMMAND,
            receive_service_request
        )
    )

    print("CyberQueen AI Bot is running...")

    app.run_polling()


if __name__ == "__main__":
    main()
