from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import logging
from typing import Optional

from config import (
    ENABLE_REPORTS, ERROR_MESSAGE,
    REPORT_SUBMITTED
)
from database.database import Database
from handlers.states import ReportStates
from handlers.keyboards import get_report_keyboard, get_admin_keyboard

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = Router()

@router.message(Command("report"))
async def start_report(message: Message, state: FSMContext):
    """Start report process.
    
    Args:
        message: Message object
        state: FSM context
    """
    try:
        if not ENABLE_REPORTS:
            await message.answer("Reporting is currently disabled.")
            return

        # Check if user has a profile
        db = Database()
        user = await db.get_user_by_telegram_id(message.from_user.id)
        if not user:
            await message.answer(
                "Please create a profile first using /profile"
            )
            return

        # Set state
        await state.set_state(ReportStates.waiting_for_user)

        # Send instructions
        await message.answer(
            "Please send the username or ID of the user you want to report.",
            reply_markup=get_report_keyboard()
        )

    except Exception as e:
        logger.error(f"Error starting report: {e}")
        await message.answer(ERROR_MESSAGE.format(error=str(e)))

@router.message(ReportStates.waiting_for_user)
async def process_reported_user(message: Message, state: FSMContext):
    """Process reported user.
    
    Args:
        message: Message object
        state: FSM context
    """
    try:
        # Get reported user
        reported_user = message.text.strip()
        if not reported_user:
            await message.answer("Please provide a valid username or ID.")
            return

        # Check if user is reporting themselves
        if reported_user == str(message.from_user.id) or reported_user == f"@{message.from_user.username}":
            await message.answer("You cannot report yourself.")
            return

        # Store reported user
        await state.update_data(reported_user=reported_user)

        # Set state
        await state.set_state(ReportStates.waiting_for_reason)

        # Send instructions
        await message.answer(
            "Please provide the reason for your report.",
            reply_markup=get_report_keyboard()
        )

    except Exception as e:
        logger.error(f"Error processing reported user: {e}")
        await message.answer(ERROR_MESSAGE.format(error=str(e)))

@router.message(ReportStates.waiting_for_reason)
async def process_report_reason(message: Message, state: FSMContext):
    """Process report reason.
    
    Args:
        message: Message object
        state: FSM context
    """
    try:
        # Get report data
        data = await state.get_data()
        reported_user = data.get("reported_user")
        reason = message.text.strip()

        if not reason:
            await message.answer("Please provide a valid reason.")
            return

        # Create report
        db = Database()
        report_data = {
            "reporter_id": message.from_user.id,
            "reported_user": reported_user,
            "reason": reason,
            "status": "pending"
        }
        report = await db.create_report(report_data)

        if not report:
            await message.answer("Failed to submit report. Please try again later.")
            return

        # Notify admins
        for admin_id in config.ADMIN_IDS:
            try:
                await message.bot.send_message(
                    admin_id,
                    f"New report submitted:\n\n"
                    f"Reporter: {message.from_user.mention_html()}\n"
                    f"Reported User: {reported_user}\n"
                    f"Reason: {reason}\n\n"
                    f"Report ID: {report['id']}",
                    reply_markup=get_admin_keyboard(report['id'])
                )
            except Exception as e:
                logger.error(f"Error notifying admin {admin_id}: {e}")

        # Clear state
        await state.clear()

        # Send confirmation
        await message.answer(
            REPORT_SUBMITTED,
            reply_markup=get_main_menu_keyboard()
        )

    except Exception as e:
        logger.error(f"Error processing report reason: {e}")
        await message.answer(ERROR_MESSAGE.format(error=str(e)))

@router.callback_query(F.data.startswith("report_"))
async def handle_report_action(callback: CallbackQuery, state: FSMContext):
    """Handle report action.
    
    Args:
        callback: Callback query
        state: FSM context
    """
    try:
        # Check if user is admin
        if callback.from_user.id not in config.ADMIN_IDS:
            await callback.answer("You don't have permission to perform this action.")
            return

        # Get report ID
        report_id = int(callback.data.split("_")[1])
        action = callback.data.split("_")[2]

        # Get report
        db = Database()
        report = await db.get_report(report_id)
        if not report:
            await callback.answer("Report not found.")
            return

        # Update report status
        if action == "approve":
            status = "reviewed"
            message = "Report approved"
        elif action == "reject":
            status = "resolved"
            message = "Report rejected"
        else:
            await callback.answer("Invalid action.")
            return

        # Update report
        success = await db.update_report(report_id, {"status": status})
        if not success:
            await callback.answer("Failed to update report.")
            return

        # Notify reporter
        try:
            await callback.bot.send_message(
                report["reporter_id"],
                f"Your report has been {status}.\n\n"
                f"Report ID: {report_id}\n"
                f"Status: {status}"
            )
        except Exception as e:
            logger.error(f"Error notifying reporter: {e}")

        # Answer callback
        await callback.answer(message)

    except Exception as e:
        logger.error(f"Error handling report action: {e}")
        await callback.answer(ERROR_MESSAGE.format(error=str(e)))

def register_handlers(dp: Dispatcher):
    """Register report handlers.
    
    Args:
        dp: Dispatcher instance
    """
    dp.include_router(router) 