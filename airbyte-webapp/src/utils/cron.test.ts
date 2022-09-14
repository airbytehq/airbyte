import { isValidCron } from "./cron";

describe("validate", () => {
  it("should not accept less than 5 symbols", () => {
    const valid = isValidCron("* * * *");
    expect(valid).toBeFalsy();
  });

  it("should not accept more than 6 symbols", () => {
    const valid = isValidCron("* * * * * * *");
    expect(valid).toBeFalsy();
  });

  it("should accept 6 symbols to support seconds if seconds option is true", () => {
    const valid = isValidCron("* * * * * *", { seconds: true });
    expect(valid).toBeTruthy();
  });

  it("should accept 6 symbols to support seconds if seconds option is true ending with a wildcard", () => {
    const valid = isValidCron("0 11 11 11 11 ?", { seconds: true });
    expect(valid).toBeTruthy();
  });

  it("should accept 5 symbols to support without seconds", () => {
    const valid = isValidCron("* * * * *");
    expect(valid).toBeTruthy();
  });

  it("should accept whitespaces on each side", () => {
    const valid = isValidCron(" * * * * * ");
    expect(valid).toBeTruthy();
  });

  it("should not accept scalar ending with a wildcard", () => {
    const wildcardAfterMinute = isValidCron("1* * * * *");
    expect(wildcardAfterMinute).toBeFalsy();

    const wildcardAfterHour = isValidCron("* 1* * * *");
    expect(wildcardAfterHour).toBeFalsy();

    const wildcardBeforeMinute = isValidCron("*1 * * * *");
    expect(wildcardBeforeMinute).toBeFalsy();

    const wildcardBeforeHour = isValidCron("* *1 * * *");
    expect(wildcardBeforeHour).toBeFalsy();
  });

  it("should not accept seconds outside of 0-59", () => {
    const at0 = isValidCron("0 * * * * *", { seconds: true });
    expect(at0).toBeTruthy();

    const at59 = isValidCron("59 * * * * *", { seconds: true });
    expect(at59).toBeTruthy();

    const above59 = isValidCron("60 * * * * *", { seconds: true });
    expect(above59).toBeFalsy();
  });

  it("should not accept minutes outside of 0-59", () => {
    const at0 = isValidCron("* 0 * * * *", { seconds: true });
    expect(at0).toBeTruthy();

    const at596Symbols = isValidCron("* 59 * * * *", { seconds: true });
    expect(at596Symbols).toBeTruthy();

    const above596Symbols = isValidCron("* 60 * * * *", { seconds: true });
    expect(above596Symbols).toBeFalsy();

    const at595Symbols = isValidCron("59 * * * *");
    expect(at595Symbols).toBeTruthy();

    const above595Symbols = isValidCron("60 * * * *");
    expect(above595Symbols).toBeFalsy();
  });

  it("should not accept hours outside of 0-23", () => {
    const at0 = isValidCron("* 0 * * *");
    expect(at0).toBeTruthy();

    const at23 = isValidCron("* 23 * * *");
    expect(at23).toBeTruthy();

    const above23 = isValidCron("* 24 * * *");
    expect(above23).toBeFalsy();
  });

  it("should not accept days outside of 1-31", () => {
    const at1 = isValidCron("* * 1 * *");
    expect(at1).toBeTruthy();

    const below1 = isValidCron("* * 0 * *");
    expect(below1).toBeFalsy();

    const at31 = isValidCron("* * 31 * *");
    expect(at31).toBeTruthy();

    const above31 = isValidCron("* * 32 * *");
    expect(above31).toBeFalsy();
  });

  it("should not accept months outside of 1-12", () => {
    const at1 = isValidCron("* * * 1 *");
    expect(at1).toBeTruthy();

    const below1 = isValidCron("* * * 0 *");
    expect(below1).toBeFalsy();

    const at12 = isValidCron("* * * 12 *");
    expect(at12).toBeTruthy();

    const above12 = isValidCron("* * * 13 *");
    expect(above12).toBeFalsy();
  });

  it("should accept month alias with the alias flag", () => {
    const jan = isValidCron("* * * jan,JAN *", { alias: true });
    expect(jan).toBeTruthy();

    const feb = isValidCron("* * * feb,FEB *", { alias: true });
    expect(feb).toBeTruthy();

    const mar = isValidCron("* * * mar,MAR *", { alias: true });
    expect(mar).toBeTruthy();

    const apr = isValidCron("* * * apr,APR *", { alias: true });
    expect(apr).toBeTruthy();

    const may = isValidCron("* * * may,MAY *", { alias: true });
    expect(may).toBeTruthy();

    const jun = isValidCron("* * * jun,JUN *", { alias: true });
    expect(jun).toBeTruthy();

    const jul = isValidCron("* * * jul,JUL *", { alias: true });
    expect(jul).toBeTruthy();

    const aug = isValidCron("* * * aug,AUG *", { alias: true });
    expect(aug).toBeTruthy();

    const sep = isValidCron("* * * sep,SEP *", { alias: true });
    expect(sep).toBeTruthy();

    const oct = isValidCron("* * * oct,OCT *", { alias: true });
    expect(oct).toBeTruthy();

    const nov = isValidCron("* * * nov,NOV *", { alias: true });
    expect(nov).toBeTruthy();

    const dec = isValidCron("* * * dec,DEC *", { alias: true });
    expect(dec).toBeTruthy();
  });

  it("should not accept month alias without the alias flag", () => {
    const valid = isValidCron("* * * jan *");
    expect(valid).toBeFalsy();
  });

  it("should not accept invalid month alias", () => {
    const valid = isValidCron("* * * january *", { alias: true });
    expect(valid).toBeFalsy();
  });

  it("should not accept month alias as steps", () => {
    const valid = isValidCron("* * * */jan *", { alias: true });
    expect(valid).toBeFalsy();
  });

  it("should not accept days of week outside of 0-6", () => {
    const at0 = isValidCron("* * * * 0");
    expect(at0).toBeTruthy();

    const at6 = isValidCron("* * * * 6");
    expect(at6).toBeTruthy();

    const at7 = isValidCron("* * * * 7");
    expect(at7).toBeFalsy();
  });

  it("should accept 7 days of week with the allowSevenAsSunday flag", () => {
    const at7 = isValidCron("* * * * 7", { allowSevenAsSunday: true });
    expect(at7).toBeTruthy();
  });

  it("should accept weekdays alias with the alias flag", () => {
    const sun = isValidCron("* * * * sun,SUN", { alias: true });
    expect(sun).toBeTruthy();

    const mon = isValidCron("* * * * mon,MON", { alias: true });
    expect(mon).toBeTruthy();

    const tue = isValidCron("* * * * tue,TUE", { alias: true });
    expect(tue).toBeTruthy();

    const wed = isValidCron("* * * * wed,WED", { alias: true });
    expect(wed).toBeTruthy();

    const thu = isValidCron("* * * * thu,THU", { alias: true });
    expect(thu).toBeTruthy();

    const fri = isValidCron("* * * * fri,FRI", { alias: true });
    expect(fri).toBeTruthy();

    const sat = isValidCron("* * * * sat,SAT", { alias: true });
    expect(sat).toBeTruthy();
  });

  it("should not accept weekdays alias without the flag", () => {
    const valid = isValidCron("* * * * sun");
    expect(valid).toBeFalsy();
  });

  it("should not accept invalid weekdays alias", () => {
    const valid = isValidCron("* * * * sunday", { alias: true });
    expect(valid).toBeFalsy();
  });

  it("should not accept weekdays alias as steps", () => {
    const valid = isValidCron("* * * * */sun", { alias: true });
    expect(valid).toBeFalsy();
  });

  it("should accepts ranges", () => {
    const validSecond = isValidCron("1-10 * * * * *", { seconds: true });
    expect(validSecond).toBeTruthy();

    const validMinute = isValidCron("1-10 * * * *");
    expect(validMinute).toBeTruthy();

    const validHour = isValidCron("* 1-10 * * *");
    expect(validHour).toBeTruthy();

    const validDay = isValidCron("* * 1-31 * *");
    expect(validDay).toBeTruthy();

    const validMonth = isValidCron("* * * 1-12 *");
    expect(validMonth).toBeTruthy();

    const validWeekday = isValidCron("* * * * 0-6");
    expect(validWeekday).toBeTruthy();
  });

  it("should accept list of ranges", () => {
    const validSecond = isValidCron("1-10,11-20,21-30 * * * * *", { seconds: true });
    expect(validSecond).toBeTruthy();

    const validMinute = isValidCron("1-10,11-20,21-30 * * * *");
    expect(validMinute).toBeTruthy();

    const validHour = isValidCron("* 1-10,11-20,21-23 * * *");
    expect(validHour).toBeTruthy();

    const validDay = isValidCron("* * 1-10,11-20,21-31 * *");
    expect(validDay).toBeTruthy();

    const validMonth = isValidCron("* * * 1-2,3-4,5-6 *");
    expect(validMonth).toBeTruthy();

    const validWeekday = isValidCron("* * * * 0-2,3-4,5-6");
    expect(validWeekday).toBeTruthy();
  });

  it("should not accept inverted ranges", () => {
    const validSecond = isValidCron("10-1,20-11,30-21 * * * * *", { seconds: true });
    expect(validSecond).toBeFalsy();

    const validMinute = isValidCron("10-1,20-11,30-21 * * * *");
    expect(validMinute).toBeFalsy();

    const validHour = isValidCron("* 10-1,20-11,23-21 * * *");
    expect(validHour).toBeFalsy();

    const validDay = isValidCron("* * 10-1,20-11,31-21 * *");
    expect(validDay).toBeFalsy();

    const validMonth = isValidCron("* * * 2-1,4-3,6-5 *");
    expect(validMonth).toBeFalsy();

    const validWeekday = isValidCron("* * * * 2-0,4-3,6-5");
    expect(validWeekday).toBeFalsy();
  });

  it("should accept steps in ranges", () => {
    const validSecond = isValidCron("1-10/2,21-30/2 * * * * *", { seconds: true });
    expect(validSecond).toBeTruthy();

    const validMinute = isValidCron("1-10/2,11-20/2 * * * *");
    expect(validMinute).toBeTruthy();

    const validHour = isValidCron("* 1-10/2,11-20/2 * * *");
    expect(validHour).toBeTruthy();

    const validDay = isValidCron("* * 1-10/2,11-20/2 * *");
    expect(validDay).toBeTruthy();

    const validMonth = isValidCron("* * * 1-2/2,3-4/2 *");
    expect(validMonth).toBeTruthy();

    const validWeekday = isValidCron("* * * * 0-2/2,3-4/2");
    expect(validWeekday).toBeTruthy();
  });

  it("should accept wildcards over steps in ranges", () => {
    const validSecond = isValidCron("1-10,*/2 * * * * *", { seconds: true });
    expect(validSecond).toBeTruthy();

    const validMinute = isValidCron("1-10,*/2 * * * *");
    expect(validMinute).toBeTruthy();

    const validHour = isValidCron("* 1-10,*/2 * * *");
    expect(validHour).toBeTruthy();

    const validDay = isValidCron("* * 1-10,*/2 * *");
    expect(validDay).toBeTruthy();

    const validMonth = isValidCron("* * * 1-2,*/2 *");
    expect(validMonth).toBeTruthy();

    const validWeekday = isValidCron("* * * * 0-2,*/2");
    expect(validWeekday).toBeTruthy();
  });

  it("should not accept steps below 1", () => {
    const validSecond = isValidCron("1-10,*/0 * * * * *", { seconds: true });
    expect(validSecond).toBeFalsy();

    const validMinute = isValidCron("1-10,*/0 * * * *");
    expect(validMinute).toBeFalsy();

    const validHour = isValidCron("* 1-10,*/0 * * *");
    expect(validHour).toBeFalsy();

    const validDay = isValidCron("* * 1-10,*/0 * *");
    expect(validDay).toBeFalsy();

    const validMonth = isValidCron("* * * 1-2,*/0 *");
    expect(validMonth).toBeFalsy();

    const validWeekday = isValidCron("* * * * 0-2,*/-1");
    expect(validWeekday).toBeFalsy();
  });

  it("should not accept an invalid range", () => {
    const validSecond = isValidCron("1-10-20 * * * * *");
    expect(validSecond).toBeFalsy();

    const validMinute = isValidCron("1-10-20 * * * *", { seconds: true });
    expect(validMinute).toBeFalsy();

    const validHour = isValidCron("* 1-10-20 * * *");
    expect(validHour).toBeFalsy();

    const validDay = isValidCron("* * 1-10-20 * *");
    expect(validDay).toBeFalsy();

    const validMonth = isValidCron("* * * 1-2-10 *");
    expect(validMonth).toBeFalsy();

    const validWeekday = isValidCron("* * * * 0-2-6");
    expect(validWeekday).toBeFalsy();
  });

  it("should not accept invalid step", () => {
    const validSecond = isValidCron("1/10/20 * * * * *", { seconds: true });
    expect(validSecond).toBeFalsy();

    const validMinute = isValidCron("1/10/20 * * * *");
    expect(validMinute).toBeFalsy();

    const validHour = isValidCron("* 1/10/20 * * *");
    expect(validHour).toBeFalsy();

    const validDay = isValidCron("* * 1/10/20 * *");
    expect(validDay).toBeFalsy();

    const validMonth = isValidCron("* * * 1/2/10 *");
    expect(validMonth).toBeFalsy();

    const validWeekday = isValidCron("* * * * 0/2/6");
    expect(validWeekday).toBeFalsy();
  });

  it("should not accept incomplete step", () => {
    const validSecond = isValidCron("*/ * * * * *", { seconds: true });
    expect(validSecond).toBeFalsy();

    const validMinute = isValidCron("*/ * * * *");
    expect(validMinute).toBeFalsy();

    const validHour = isValidCron("* */ * * *");
    expect(validHour).toBeFalsy();

    const validDay = isValidCron("* * */ * *");
    expect(validDay).toBeFalsy();

    const validMonth = isValidCron("* * * /* *");
    expect(validMonth).toBeFalsy();

    const validWeekday = isValidCron("* * * * */");
    expect(validWeekday).toBeFalsy();
  });

  it("should not accept wildcards as range value", () => {
    const validSecond = isValidCron("1-* * * * * *", { seconds: true });
    expect(validSecond).toBeFalsy();

    const validMinute = isValidCron("1-* * * * *");
    expect(validMinute).toBeFalsy();

    const validHour = isValidCron("* 1-* * * *");
    expect(validHour).toBeFalsy();

    const validDay = isValidCron("* * 1-* * *");
    expect(validDay).toBeFalsy();

    const validMonth = isValidCron("* * * 1-* *");
    expect(validMonth).toBeFalsy();

    const validWeekday = isValidCron("* * * * 0-*");
    expect(validWeekday).toBeFalsy();
  });

  it("should not accept invalid range", () => {
    const validSecond = isValidCron("1- * * * * *", { seconds: true, alias: true });
    expect(validSecond).toBeFalsy();

    const validMinute = isValidCron("1- * * * *");
    expect(validMinute).toBeFalsy();

    const validHour = isValidCron("* - * * *");
    expect(validHour).toBeFalsy();

    const validDay = isValidCron("* * 1- * *");
    expect(validDay).toBeFalsy();

    const validMonth = isValidCron("* * * -1 *");
    expect(validMonth).toBeFalsy();

    const validWeekday = isValidCron("* * * * 0-");
    expect(validWeekday).toBeFalsy();
  });

  it("should accept everything combined", () => {
    const valid = isValidCron(
      // tslint:disable-next-line:max-line-length
      "10,*/15,12-14,15-30/5 10,*/15,12-14,15-30/5 10,*/12,12-14,5-10/2 10,*/7,12-15,15-30/5 1,*/3,4-5,jun-oct/2 0,*/3,2-4,mon-fri/2",
      { seconds: true, alias: true }
    );
    expect(valid).toBeTruthy();
  });

  it("should accept number prefixed with a 0", () => {
    const valid = isValidCron("05 05 * * *");
    expect(valid).toBeTruthy();
  });

  it("should not accept question marks in days if allowBlankDay is not set", () => {
    const dayValid = isValidCron("* * ? * *");
    expect(dayValid).toBeFalsy();

    const weekDayValid = isValidCron("* * * * ?");
    expect(weekDayValid).toBeFalsy();

    const bothValid = isValidCron("* * ? * ?");
    expect(bothValid).toBeFalsy();
  });

  it("should accept question marks in days if allowBlankDay is set", () => {
    const valid = isValidCron("* * ? * *", { allowBlankDay: true });
    expect(valid).toBeTruthy();
  });

  it("should accept question marks in weekdays", () => {
    const valid = isValidCron("* * * * ?", { allowBlankDay: true });
    expect(valid).toBeTruthy();

    const validWithAliases = isValidCron("* * * * ?", { alias: true, allowBlankDay: true });
    expect(validWithAliases).toBeTruthy();
  });

  it("should not accept question marks in days and weekdays at the same time if allowBlankDay is set", () => {
    const valid = isValidCron("* * ? * ?", { allowBlankDay: true });
    expect(valid).toBeFalsy();

    const validWithAliases = isValidCron("* * ? * ?", { alias: true, allowBlankDay: true });
    expect(validWithAliases).toBeFalsy();
  });
});
