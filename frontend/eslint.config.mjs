import angular from '@angular-eslint/eslint-plugin';
import angularTemplate from '@angular-eslint/eslint-plugin-template';
import angularTemplateParser from '@angular-eslint/template-parser';
import tseslint from '@typescript-eslint/eslint-plugin';
import tsparser from '@typescript-eslint/parser';

export default [
    {
        ignores: [
            'node_modules/**',
            'dist/**',
            '.angular/**',
            'coverage/**',
            '**/*.js'
        ]
    },
    {
        files: ['**/*.ts'],
        languageOptions: {
            parser: tsparser,
            parserOptions: {
                project: './tsconfig.json',
                ecmaVersion: 2022,
                sourceType: 'module'
            }
        },
        plugins: {
            '@typescript-eslint': tseslint,
            '@angular-eslint': angular
        },
        rules: {
            ...tseslint.configs.recommended.rules,
            ...angular.configs.recommended.rules,
            '@angular-eslint/directive-selector': [
                'error',
                {
                    type: 'attribute',
                    prefix: 'app',
                    style: 'camelCase'
                }
            ],
            '@angular-eslint/component-selector': [
                'error',
                {
                    type: 'element',
                    prefix: 'app',
                    style: 'kebab-case'
                }
            ],
            '@typescript-eslint/no-explicit-any': 'warn',
            '@typescript-eslint/explicit-function-return-type': 'off',
            '@typescript-eslint/no-unused-vars': ['error', { 'argsIgnorePattern': '^_' }]
        }
    },
    {
        files: ['**/*.html'],
        languageOptions: {
            parser: angularTemplateParser
        },
        plugins: {
            '@angular-eslint/template': angularTemplate
        },
        rules: {
            ...angularTemplate.configs.recommended.rules,
            ...angularTemplate.configs.accessibility.rules
        }
    }
];
