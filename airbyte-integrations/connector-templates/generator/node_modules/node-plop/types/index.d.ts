import inquirer from 'inquirer';
// @types/globby doesn't export types for GlobOptions, so we have to work a little bit to extract them:
// GlobOptions is the second parameter of the sync function, which can be extracted with the Parameters<T> type
import {globbySync} from 'globby';

type GlobOptions = Parameters<typeof globbySync>[1];
import {HelperDelegate as HelperFunction} from 'handlebars';

export interface IncludeDefinitionConfig {
    generators?: boolean;
    helpers?: boolean;
    partials?: boolean;
    actionTypes?: boolean;
}

export type IncludeDefinition =
    | boolean
    | string[]
    | IncludeDefinitionConfig;

export interface NodePlopAPI {
    setGenerator(name: string, config: Partial<PlopGeneratorConfig>): PlopGenerator;

    setPrompt(name: string, prompt: inquirer.prompts.PromptConstructor): void;

    setWelcomeMessage(message: string): void;

    getWelcomeMessage(): string;

    getGenerator(name: string): PlopGenerator;

    getGeneratorList(): { name: string; description: string }[];

    setPartial(name: string, str: string): void;

    getPartial(name: string): string;

    getPartialList(): string[];

    setHelper(name: string, fn: HelperFunction): void;

    // eslint-disable-next-line @typescript-eslint/ban-types
    getHelper(name: string): Function;

    getHelperList(): string[];

    setActionType(name: string, fn: CustomActionFunction): void;

    /**
     * This does not include a `CustomActionConfig` for the same reasons
     * Listed in the `ActionType` declaration. Please see that JSDoc for more
     */
    getActionType(name: string): ActionType;

    getActionTypeList(): string[];

    setPlopfilePath(filePath: string): void;

    getPlopfilePath(): string;

    getDestBasePath(): string;

    // plop.load functionality
    load(target: string[] | string, loadCfg?: Partial<PlopCfg> | null, includeOverride?: IncludeDefinition): Promise<void>;

    setDefaultInclude(inc: object): void;

    getDefaultInclude(): object;

    renderString(template: string, data: any): string; //set to any matching handlebars declaration

    // passthroughs for backward compatibility
    /**
     * @deprecated Use "setPrompt" instead. This will be removed in the next major release
     */
    addPrompt(name: string, prompt: inquirer.PromptModule): void;

    /**
     * @deprecated Use "setPartial" instead. This will be removed in the next major release
     */
    addPartial(name: string, str: string): void;

    /**
     * @deprecated Use "setHelper" instead. This will be removed in the next major release
     */
    // eslint-disable-next-line @typescript-eslint/ban-types
    addHelper(name: string, fn: Function): void;
}

interface PlopActionHooksFailures {
    type: string;
    path: string;
    error: string;
    message: string;
}

interface PlopActionHooksChanges {
    type: string;
    path: string;
}

interface PlopActionHooks {
    onComment?: (msg: string) => void;
    onSuccess?: (change: PlopActionHooksChanges) => void;
    onFailure?: (failure: PlopActionHooksFailures) => void;
}

export interface PlopGeneratorConfig {
    description: string;
    prompts: Prompts;
    actions: Actions;
}

export interface PlopGenerator extends PlopGeneratorConfig {
    runPrompts: (bypassArr?: string[]) => Promise<any>;
    runActions: (
        answers: inquirer.Answers,
        hooks?: PlopActionHooks
    ) => Promise<{
        changes: PlopActionHooksChanges[];
        failures: PlopActionHooksFailures[];
    }>;
}

export type PromptQuestion = inquirer.Question
    | inquirer.CheckboxQuestion
    | inquirer.ListQuestion
    | inquirer.ExpandQuestion
    | inquirer.ConfirmQuestion
    | inquirer.EditorQuestion
    | inquirer.RawListQuestion
    | inquirer.PasswordQuestion
    | inquirer.NumberQuestion
    | inquirer.InputQuestion;

export type DynamicPromptsFunction = (inquirer: inquirer.Inquirer) => Promise<inquirer.Answers>;
export type DynamicActionsFunction = (data?: inquirer.Answers) => ActionType[];

export type Prompts = DynamicPromptsFunction | PromptQuestion[]
export type Actions = DynamicActionsFunction | ActionType[];

interface Template {
    template: string;
    templateFile?: never;
}

interface TemplateFile {
    template?: never;
    templateFile: string;
}

type TemplateStrOrFile = Template | TemplateFile;

/**
 * "TypeString" is a type generic of what type is present. It allows us
 * to pass arbitrary keys to a field alongside any type name that doesn't
 * intersect with built-ins. This is an unfortunate limitation of TypeScript
 *
 * We strongly suggest you actually use a const type (so, 'customActionName' instead of `string`),
 * that way, you can make sure that your custom action doesn't interfere with built-ins in
 * the future.
 *
 * However, keep in mind that by doing so it means your config object MUST have the same `type` value
 * as the generic input string.
 *
 * To ignore this limitation, simply pass "string"
 */
export interface CustomActionConfig<TypeString extends string> extends Omit<ActionConfig, 'type'> {
    type: TypeString extends 'addMany' |
        'modify' |
        'append' ? never : TypeString;

    [key: string]: any;
}

export type CustomActionFunction = (
    answers: inquirer.Answers,
    config: CustomActionConfig<string>,
    plopfileApi: NodePlopAPI
) => Promise<string> | string;

/**
 * Ideally, we'd have `CustomActionConfig` here,
 * but if we do, we lose the ability to strictly type an action,
 * since "type: 'append'" is now considered a custom action config
 * and not an append action config.
 *
 * See `CustomActionConfig` declaration for more usage instructions
 *
 * If you know of a solution, please open a GitHub issue to discuss
 */
export type ActionType =
    | string
    | ActionConfig
    | AddActionConfig
    | AddManyActionConfig
    | ModifyActionConfig
    | AppendActionConfig
    | CustomActionFunction;

export interface ActionConfig {
    type: string;
    force?: boolean;
    data?: object;
    abortOnFail?: boolean;
    // eslint-disable-next-line @typescript-eslint/ban-types
    skip?: Function;
}

type TransformFn<T> = (template: string, data: any, cfg: T) => string | Promise<string>;

interface AddActionConfigBase extends ActionConfig {
    type: 'add';
    path: string;
    skipIfExists?: boolean;
    transform?: TransformFn<AddActionConfig>;
}

export type AddActionConfig = AddActionConfigBase & TemplateStrOrFile;

export interface AddManyActionConfig extends Pick<AddActionConfig, Exclude<keyof AddActionConfig, 'type' | 'templateFile' | 'template' | 'transform'>> {
    type: 'addMany';
    destination: string;
    base: string;
    templateFiles: string | string[];
    stripExtensions?: string[];
    globOptions: GlobOptions;
    verbose?: boolean;
    transform?: TransformFn<AddManyActionConfig>;
}

interface ModifyActionConfigBase extends ActionConfig {
    type: 'modify';
    path: string;
    pattern: string | RegExp;
    transform?: TransformFn<ModifyActionConfig>;
}

export type ModifyActionConfig = ModifyActionConfigBase & TemplateStrOrFile;

interface AppendActionConfigBase extends ActionConfig {
    type: 'append';
    path: string;
    pattern: string | RegExp;
    unique: boolean;
    separator: string;
}

export type AppendActionConfig = AppendActionConfigBase & TemplateStrOrFile;

export interface PlopCfg {
    force: boolean;
    destBasePath: string | undefined;
}

declare function nodePlop(plopfilePath?: string, plopCfg?: PlopCfg): Promise<NodePlopAPI>;

export default nodePlop;
